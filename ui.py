import os
import logging
from colorama import Fore, Style
from dnd_adventure.lore_manager import LoreManager
from dnd_adventure.console_utils import console_print, console_input

logger = logging.getLogger(__name__)

def display_status(game):
    """Display detailed player status, including stats, traits, and features, only if show_status is True."""
    if not game.show_status:
        return
    player_data = game.player.to_dict()
    stats = player_data["stats"]
    modifiers = {
        "Strength": (stats["Strength"] - 10) // 2,
        "Dexterity": (stats["Dexterity"] - 10) // 2,
        "Constitution": (stats["Constitution"] - 10) // 2,
        "Intelligence": (stats["Intelligence"] - 10) // 2,
        "Wisdom": (stats["Wisdom"] - 10) // 2,
        "Charisma": (stats["Charisma"] - 10) // 2,
    }
    hp = player_data.get("hit_points", 6 + modifiers["Constitution"])
    max_hp = player_data.get("max_hit_points", hp)
    mp = player_data.get("mp", 0)
    max_mp = player_data.get("max_mp", 0)
    spells = ", ".join(player_data["spells"].get(0, []) + player_data["spells"].get(1, [])) or "None"
    console_print(f"\n=== Character Sheet ===", color="cyan")
    console_print(f"Name: {player_data['name']}", color="cyan")
    console_print(f"Race: {player_data['race']} ({player_data['subrace'] or 'None'})", color="cyan")
    console_print(f"Class: {player_data['class']} (Level {player_data['level']})", color="cyan")
    console_print(f"HP: {hp}/{max_hp}", color="cyan")
    console_print(f"MP: {mp}/{max_mp}", color="cyan")
    console_print(f"Position: {game.player_pos} in room {game.current_room}", color="cyan")
    console_print("\nStats:", color="cyan")
    for stat, value in stats.items():
        mod = modifiers[stat]
        console_print(f"  {stat}: {value} (Modifier: {mod:+d})", color="cyan")
    console_print("\nRacial Traits:", color="cyan")
    race_data = next(r for r in game.races if r["name"] == player_data["race"])
    subrace_data = next((sr for sr in race_data["subraces"].items() if sr[0] == player_data["subrace"]), None)
    for trait in race_data["racial_traits"]:
        console_print(f"  {trait['name']}: {trait['description']}", color="cyan")
    if subrace_data:
        for trait in subrace_data[1]["racial_traits"]:
            console_print(f"  {trait['name']}: {trait['description']}", color="cyan")
    console_print("\nClass Features:", color="cyan")
    class_data = game.classes[player_data["class"]]
    for feature in class_data["features"]:
        console_print(f"  {feature['name']}: {feature['description']}", color="cyan")
    console_print(f"\nSpells: {spells}", color="cyan")
    logger.debug(f"Displayed status for {player_data['name']}")
    console_input("Press Enter to continue...", color="yellow")

class UIManager:
    def __init__(self, game):
        self.game = game
        self.themes_dir = os.path.join(os.path.dirname(__file__), 'data', 'themes')
        self.lore_manager = LoreManager(self.themes_dir)

    def display_lore_screen(self, theme: str):
        """Display the lore intro on a standalone screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.lore_manager.print_lore(theme)
        console_input("Press Enter to continue...", color="yellow")
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_current_map(self):
        """Display the current game map."""
        room = self.game.game_world.get_room(self.game.current_room)
        if not room:
            console_print(f"Error: No room found for ID {self.game.current_room}!", color="red")
            logger.error(f"No room found for ID {self.game.current_room}")
            return
        if not self.game.current_room:
            console_print("Error: Current room is None!", color="red")
            logger.error("Current room is None")
            return
        console_print(f"You are in {room.name}.", color="cyan")
        console_print(room.description, color="cyan")
        if room.npcs:
            console_print(f"NPCs present: {', '.join(npc.name for npc in room.npcs)}", color="cyan")
        if room.exits:
            console_print(f"Exits: {', '.join(f'{direction} to {room_id}' for direction, room_id in room.exits.items())}", color="cyan")
        else:
            console_print("No visible exits.", color="cyan")
        # Render map
        map_data = self.game.graphics["maps"].get(self.game.current_map, {})
        if not map_data:
            console_print(f"Error: Map {self.game.current_map} not found in graphics!", color="red")
            logger.error(f"Map {self.game.current_map} not found")
            return
        map_grid = [["▓" for _ in range(5)] for _ in range(5)]
        player_x, player_y = self.game.player_pos
        map_grid[player_y][player_x] = "@"
        if room.exits:
            for direction, _ in room.exits.items():
                if direction == "south":
                    map_grid[4][4] = "+"
                elif direction == "north":
                    map_grid[0][4] = "+"
                elif direction == "east":
                    map_grid[4][4] = "+"
                elif direction == "west":
                    map_grid[4][0] = "+"
        for row in map_grid:
            console_print("".join(row), color="cyan")
        console_print(f"Mode: {'Movement (WASD to move, Enter for commands)' if self.game.mode == 'movement' else 'Command (type command, Enter to submit, double Enter to return to movement)'}", color="yellow")
        logger.debug(f"Displayed map: map={self.game.current_map}, room={self.game.current_room}, pos={self.game.player_pos}")