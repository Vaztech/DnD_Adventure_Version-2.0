# dnd_adventure/game.py
import logging
import time
from typing import Optional, List
from colorama import Fore, Style

# ✅ Robust import for PlayerManager (works whether it's a top-level sibling
# package or vendored inside dnd_adventure/)
try:
    # When 'player_manager' is a top-level sibling folder to dnd_adventure/
    from player_manager.player_manager import PlayerManager
except ModuleNotFoundError:
    # When 'player_manager' is inside dnd_adventure/player_manager/
    from .player_manager.player_manager import PlayerManager

from dnd_adventure.movement_handler import MovementHandler
from dnd_adventure.combat_manager import CombatManager
from dnd_adventure.lore_manager import LoreManager
from dnd_adventure.save_manager import SaveManager
from dnd_adventure.ui import UIManager
from dnd_adventure.world import World
from dnd_adventure.game_world import GameWorld
from dnd_adventure.quest_manager import QuestManager
from dnd_adventure.utils import load_graphics
import json
import os
import random

logger = logging.getLogger(__name__)

class Game:
    def __init__(self, player_name: str, player_manager: PlayerManager, save_file: Optional[str] = None):
        logger.debug(f"Initializing Game object for player: {player_name}")
        print("DEBUG: Initializing Game...")
        self.player_name = player_name
        self.graphics = load_graphics()
        self.world = World(seed=None, graphics=self.graphics)

        classes_path = os.path.join(os.path.dirname(__file__), 'data', 'classes.json')
        logger.debug(f"Loading classes from {classes_path}...")
        try:
            with open(classes_path, 'r') as f:
                self.classes = json.load(f)
            logger.debug(f"Loaded classes: {self.classes}")
        except FileNotFoundError:
            logger.error(f"Classes file not found at {classes_path}")
            self.classes = []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding classes.json: {e}")
            self.classes = []

        theme = "fantasy" if not save_file else self._get_theme_from_save(save_file)
        self.game_world = GameWorld(self.world, character_name=self.player_name.lower(), theme=theme)
        self.world_state = self.game_world.world_state

        self.player, self.starting_room = player_manager.initialize_player(self, save_file)
        if self.player is None:
            logger.error("Game cannot start without a player")
            self.running = False
            print(f"{Fore.YELLOW}Game cannot start without a character. Returning to main menu.{Style.RESET_ALL}")
            return

        # If your PlayerManager exposes race data differently, adjust this line accordingly
        self.races = getattr(player_manager, "race_manager", getattr(player_manager, "races", None))
        if hasattr(self.races, "races"):
            # handle case where race_manager has a .races list
            self.races = self.races.races

        self.quest_manager = QuestManager(self.world)
        self.movement_handler = MovementHandler(self)
        self.combat_manager = CombatManager(self)

        themes_dir = os.path.join(os.path.dirname(__file__), 'data', 'themes')
        self.lore_manager = LoreManager(themes_dir)
        self.save_manager = SaveManager()
        self.ui_manager = UIManager(self)
        self.ui_manager.display_lore_screen(theme)

        self.current_room = self._get_starting_room()
        self.player_pos = (2, 2)
        self.running = True
        self.mode = "movement"
        self.debug_mode = False
        self.previous_menu = None
        self.commands = [
            "look", "lore", "attack", "cast", "rest", "talk",
            "quest list", "quest start", "quest complete", "save", "quit", "exit", "character"
        ]
        self.current_map = None
        self.last_world_pos = self.player_pos
        self.message = ""
        self.last_enter_time = 0
        self.last_key_time = 0.0
        self.show_status = False

        room = self.game_world.get_room(self.current_room)
        if room and room.room_type.value in self.graphics["maps"]:
            self.current_map = room.room_type.value
        else:
            self.current_map = "dungeon"

        logger.debug(f"Game initialized: map={self.current_map}, room={self.current_room}, pos={self.player_pos}")

    def _get_theme_from_save(self, save_file: str) -> str:
        try:
            save_data = self.save_manager.load_game(save_file)
            return save_data.get("theme", "fantasy")
        except Exception as e:
            logger.error(f"Failed to load theme from save {save_file}: {e}")
            return "fantasy"

    def _get_starting_room(self) -> str:
        if self.world_state.civilizations:
            civ = random.choice(self.world_state.civilizations)
            x, y = civ['capital']['x'], civ['capital']['y']
            logger.debug(f"Selected capital at ({x}, {y}) as starting room")
            return f"{x},{y}"
        logger.warning("No civilizations found, defaulting to (0, 0)")
        return "0,0"

    @staticmethod
    def list_save_files() -> List[str]:
        saves_dir = os.path.join(os.path.dirname(__file__), '..', 'saves')
        try:
            if not os.path.exists(saves_dir):
                os.makedirs(saves_dir)
            save_files = [f for f in os.listdir(saves_dir) if f.endswith('.save')]
            logger.debug(f"Found save files: {save_files}")
            return save_files
        except Exception as e:
            logger.error(f"Error listing save files: {e}")
            return []

    def handle_command(self, cmd: str):
        self.message = ""
        logger.debug(f"Handling command: {cmd}")
        cmd = cmd.lower().strip()

        if cmd in ["w", "s", "a", "d"]:
            if self.mode == "movement":
                logger.debug(f"Processing movement command: {cmd}")
                self.movement_handler.handle_movement(cmd)
                logger.debug(f"Player position after movement: {self.player_pos}")
            else:
                self.message = (
                    f"{Fore.RED}Movement command '{cmd}' not allowed in command mode. "
                    f"Press Enter twice to return to movement mode.{Style.RESET_ALL}"
                )
                logger.warning(f"Movement command '{cmd}' attempted in command mode")

        elif cmd == "look":
            self.ui_manager.display_current_map()

        elif cmd == "lore":
            theme = self.player.to_dict().get("theme", "fantasy")
            self.ui_manager.display_lore_screen(theme)

        elif cmd == "attack":
            self.combat_manager.handle_attack_command()

        elif cmd.startswith("cast "):
            self.combat_manager.handle_cast_command(cmd)

        elif cmd == "cast list":
            self.combat_manager.print_spell_list()

        elif cmd == "rest":
            self.combat_manager.handle_rest_command()

        elif cmd == "talk":
            room = self.game_world.get_room(self.current_room)
            if room and hasattr(room, 'npcs') and room.npcs:
                self.message = room.npcs[0].talk()
            else:
                self.message = f"{Fore.YELLOW}No one to talk to here!{Style.RESET_ALL}"

        elif cmd == "quest list":
            self.quest_manager.quest_list()

        elif cmd.startswith("quest start "):
            try:
                quest_id = int(cmd.split()[-1])
                self.quest_manager.start_quest(quest_id)
            except ValueError:
                self.message = f"{Fore.RED}Invalid quest ID. Use 'quest start <number>'.{Style.RESET_ALL}"
                logger.warning(f"Invalid quest ID: {cmd}")

        elif cmd == "quest complete":
            for quest in self.quest_manager.active_quests:
                self.quest_manager.complete_quest(
                    quest["id"], self.player, self.last_world_pos, self.current_room
                )

        elif cmd == "save":
            save_data = self.player.to_dict()
            save_data["current_room"] = self.current_room
            save_data["player_pos"] = list(self.last_world_pos)
            save_data["world_seed"] = None
            self.save_manager.save_game(
                save_data,
                f"{self.player_name.lower().replace(' ', '_')}_{int(time.time())}.save"
            )
            self.message = f"{Fore.GREEN}Game saved!{Style.RESET_ALL}"

        elif cmd in ["quit", "exit"]:
            self.running = False
            logger.info("Game quit by user")

        elif cmd in ["north", "south", "east", "west", "n", "s", "e"]:
            self.message = f"{Fore.RED}Movement is controlled with arrow keys or WASD only.{Style.RESET_ALL}"
            logger.debug(f"Attempted movement command: {cmd}")

        elif cmd == "help":
            self.message = f"{Fore.YELLOW}Available commands: {', '.join(self.commands)}{Style.RESET_ALL}"
            logger.debug("Displayed help commands")

        elif cmd == "debug":
            self.debug_mode = not self.debug_mode
            self.message = f"Debug mode: {'ON' if self.debug_mode else 'OFF'}"

        elif cmd == "clear path" and self.debug_mode:
            tile_key = "101,96"
            self.world.map["locations"][tile_key] = {"type": "forest"}
            self.message = "Path cleared at (101, 96)"

        elif cmd == "character":
            self.show_status = True
            self.ui_manager.display_current_map()
            from dnd_adventure.ui import display_status
            display_status(self)
            self.show_status = False
            logger.debug(f"Displayed character sheet for {self.player.to_dict()['name']}")

        elif cmd:
            self.message = (
                f"{Fore.RED}Unknown command '{cmd}'. "
                f"Try: {', '.join(self.commands)}{Style.RESET_ALL}"
            )
            logger.warning(f"Unknown command: {cmd}")
