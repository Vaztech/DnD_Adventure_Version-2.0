import os
import json
import logging
import random
from typing import Optional, Tuple, Any, Dict, List
from .race_manager import RaceManager
from .class_manager import ClassManager
from .stat_manager import StatManager
from .spell_manager import SpellManager
from .feature_manager import FeatureManager
from .stat_calculator import StatCalculator
from .console_utils import console_print, console_input
from dnd_adventure.player import Player

logger = logging.getLogger(__name__)

class PlayerManager:
    def __init__(self):
        self.race_manager = RaceManager()
        self.class_manager = ClassManager()
        self.stat_manager = StatManager()
        self.spell_manager = SpellManager()
        self.feature_manager = FeatureManager()
        self.stat_calculator = StatCalculator()
        self.themes = self.load_themes()

    def load_themes(self):
        themes_dir = os.path.join(os.path.dirname(__file__), '..', 'dnd_adventure', 'data', 'themes')
        themes = []
        if os.path.exists(themes_dir):
            for filename in os.listdir(themes_dir):
                if filename.endswith('.json'):
                    themes.append(filename.replace('.json', ''))
        return themes

    def initialize_player(self, game: Any, save_file: Optional[str] = None) -> Tuple[Optional[Player], Optional[str]]:
        logger.debug(f"Initializing player, save_file={save_file}")
        if save_file:
            try:
                player_data = game.save_manager.load_game(save_file)
                if player_data:
                    if isinstance(player_data["stats"], list):
                        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
                        player_data["stats"] = dict(zip(stat_names, player_data["stats"]))
                    player = Player(
                        name=player_data["name"],
                        race=player_data["race"],
                        subrace=player_data["subrace"],
                        character_class=player_data["class"],
                        stats=player_data["stats"],
                        spells=player_data.get("spells", {0: [], 1: []}),
                        level=player_data.get("level", 1),
                        features=player_data.get("features", []),
                        subclass=player_data.get("subclass", None),
                        hit_points=player_data.get("hit_points", 1),
                        max_hit_points=player_data.get("max_hit_points", 1),
                        mp=player_data.get("mp", 0),
                        max_mp=player_data.get("max_mp", 0),
                        xp=player_data.get("xp", 0),
                    )
                    starting_room = player_data.get("current_room")
                    logger.debug(f"Loaded player: {player_data['name']}, room: {starting_room}")
                    return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                console_print("Failed to load save file. Starting new character.", color="red")
        
        logger.debug("Creating new player")
        console_print("Creating new character...", color="cyan")
        player_data = self._create_character(game)
        if not player_data:
            logger.error("Character creation failed")
            return None, None
        
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        stats_dict = dict(zip(stat_names, player_data["stats"]))
        
        player = Player(
            name=game.player_name,
            race=player_data["race"],
            subrace=player_data["subrace"],
            character_class=player_data["class"],
            stats=stats_dict,
            spells=player_data["spells"],
            level=player_data.get("level", 1),
            features=player_data["features"],
            subclass=player_data.get("subclass", None),
            hit_points=player_data["max_hp"],
            max_hit_points=player_data["max_hp"],
            mp=player_data["max_mp"],
            max_mp=player_data["max_mp"],
            xp=0,
        )
        starting_room = self.find_starting_position(game)
        logger.debug("Player initialization complete")
        logger.info(
            f"Character created: {player.name}, {player.race}, {player.subrace}, {player.character_class}, level {player.level}, subclass {player.subclass}, theme {player_data.get('theme')}"
        )
        return player, starting_room

    def _create_character(self, game: Any) -> Optional[Dict[str, Any]]:
        logger.debug("Starting character creation")
        race = None
        subrace = None
        character_class = None
        subclass = None
        stats = None
        spells = {0: [], 1: []}
        features = []
        level = 1
        theme = None

        while True:
            if not theme:
                theme = self.select_theme()
                if not theme:
                    logger.debug("Character creation cancelled during theme selection")
                    return None

            if not race:
                race = self.race_manager.select_race()
                if not race:
                    logger.debug("Character creation cancelled during race selection")
                    return None
                subrace = self.race_manager.select_subrace(race)
            
            if not character_class:
                character_class = self.class_manager.select_class(game)
                if not character_class:
                    logger.debug("Character creation cancelled during class selection")
                    return None
                subclass = self.class_manager.select_subclass(game, character_class, level)
            
            if not stats:
                stats = self.stat_manager.choose_stats(race, subrace, character_class)
            
            race_dict = self.race_manager.get_race_data(race)
            subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
            race_modifiers = race_dict.get("ability_modifiers", {})
            subrace_modifiers = subrace_dict.get("ability_modifiers", {})
            
            combined_modifiers = {}
            for stat, value in race_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            for stat, value in subrace_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            
            stat_dict = {
                "Strength": stats[0],
                "Dexterity": stats[1],
                "Constitution": stats[2],
                "Intelligence": stats[3],
                "Wisdom": stats[4],
                "Charisma": stats[5],
            }
            for stat, value in combined_modifiers.items():
                stat_dict[stat] = stat_dict.get(stat, 6) + value
            final_stats = [
                stat_dict["Strength"], stat_dict["Dexterity"], stat_dict["Constitution"],
                stat_dict["Intelligence"], stat_dict["Wisdom"], stat_dict["Charisma"]
            ]
            
            class_data = game.classes.get(character_class, {})
            
            spells = {0: [], 1: []}
            if class_data.get("spellcasting"):
                spells = self.spell_manager.select_spells(game, character_class, level, stat_dict)
            
            if not features:
                features = self.feature_manager.get_class_features(game, character_class)
            
            max_hp = self.stat_calculator.calculate_hp(class_data, stat_dict)
            current_hp = max_hp
            max_mp = self.stat_calculator.calculate_mp(class_data, stat_dict)
            current_mp = max_mp
            attack = self.stat_calculator.calculate_attack(class_data, stat_dict)
            defense = self.stat_calculator.calculate_defense(stat_dict)
            
            self._display_character_summary(
                game.player_name, level, race, subrace, combined_modifiers, current_hp, max_hp,
                current_mp, max_mp, attack, defense, character_class, stats, race_modifiers,
                subrace_modifiers, class_data, features, spells, stat_dict
            )
            
            choice = self._confirm_character()
            logger.debug(f"Confirmation menu choice: {choice}")
            if choice == '1':
                race = None
                subrace = None
                spells = {0: [], 1: []}
                continue
            elif choice == '2':
                character_class = None
                subclass = None
                spells = {0: [], 1: []}
                features = []
                continue
            elif choice == '3':
                if class_data.get("spellcasting"):
                    spells = self.spell_manager.select_spells(game, character_class, level, stat_dict)
                else:
                    console_print("This class cannot cast spells.", color="red")
                continue
            elif choice == '4':
                stats = None
                continue
            elif choice == '5':
                logger.debug(
                    f"Character confirmed: {{'theme': '{theme}', 'race': '{race}', 'subrace': '{subrace}', 'class': '{character_class}', "
                    f"'subclass': '{subclass}', 'stats': {stats}, 'final_stats': {final_stats}, 'spells': {spells}, 'features': {features}, 'level': {level}}}"
                )
                return {
                    "theme": theme,
                    "race": race,
                    "subrace": subrace,
                    "class": character_class,
                    "subclass": subclass,
                    "stats": final_stats,
                    "stat_dict": stat_dict,
                    "spells": spells,
                    "features": features,
                    "level": level,
                    "max_hp": max_hp,
                    "max_mp": max_mp,
                }
            else:
                console_print("Invalid choice. Please select 1-5.", color="red")

    def select_theme(self) -> Optional[str]:
        if not self.themes:
            logger.error("No themes found in data/themes")
            console_print("No themes available. Defaulting to fantasy.", color="yellow")
            return "fantasy"
        console_print("\nSelect World Theme:", color="cyan")
        for i, theme in enumerate(self.themes, 1):
            console_print(f"{i}. {theme.capitalize()}", color="cyan")
        choice = console_input("Enter choice (1-{}): ".format(len(self.themes)), color="yellow")
        try:
            return self.themes[int(choice) - 1]
        except (ValueError, IndexError):
            logger.warning("Invalid theme choice, defaulting to fantasy")
            console_print("Invalid choice. Defaulting to fantasy.", color="yellow")
            return "fantasy"

    def _display_character_summary(
        self, name: str, level: int, race: str, subrace: Optional[str],
        combined_modifiers: Dict, current_hp: int, max_hp: int, current_mp: int,
        max_mp: int, attack: int, defense: int, character_class: str,
        stats: List[int], race_modifiers: Dict, subrace_modifiers: Dict,
        class_data: Dict, features: List[str], spells: Dict, stat_dict: Dict[str, int]
    ):
        console_print("=== Character Summary ===", color="cyan")
        console_print(f"Name: {name}", color="cyan")
        console_print(f"Level: {level}", color="cyan")
        console_print(f"Class: {character_class}", color="cyan")
        console_print(f"Race: {race} ({subrace or 'None'})", color="cyan")
        console_print(f"Racial Stat Bonus: {self.race_manager.format_modifiers(combined_modifiers) or 'None'}", color="cyan")
        console_print(f"HP: {current_hp}/{max_hp}", color="cyan")
        console_print(f"MP: {current_mp}/{max_mp}", color="cyan")
        console_print(f"Attack Bonus: {attack}  # Added to your d20 roll when attacking to hit enemies", color="cyan")
        console_print(f"AC: {defense}  # Armor Class; enemies must roll this or higher to hit you", color="cyan")
        console_print("\n=== Rolling Stats ===", color="cyan")
        for stat, value in zip(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"], stats):
            console_print(f"{stat}: {value}", color="cyan")
        console_print("\n=== Applying Bonuses ===", color="cyan")
        console_print(f"Racial Bonuses ({race}):", color="cyan")
        race_modifier_str = self.race_manager.format_modifiers(race_modifiers)
        console_print(f"  {race_modifier_str or 'None'}", color="cyan")
        console_print(f"Subrace Bonuses ({subrace or 'None'}):", color="cyan")
        subrace_modifier_str = self.race_manager.format_modifiers(subrace_modifiers)
        console_print(f"  {subrace_modifier_str or 'None'}", color="cyan")
        console_print(f"Class Bonuses ({character_class}):", color="cyan")
        console_print(f"  Class Skills: {', '.join(class_data.get('class_skills', [])) or 'None'}", color="cyan")
        console_print("  Features:", color="cyan")
        for feature in features:
            feature_desc = next((f['description'] for f in class_data.get('features', []) if f['name'] == feature), '')
            console_print(f"    - {feature}: {feature_desc}", color="cyan")
        console_print("\nAvailable Subclasses at Level 1:", color="cyan")
        subclasses = class_data.get('subclasses', {})
        if subclasses:
            for subclass_name, data in subclasses.items():
                prereqs = data.get('prerequisites', {})
                level_req = prereqs.get('level', 1)
                stat_reqs = prereqs.get('stats', {})
                meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
                status = "Unlocked" if level_req == 1 and meets_stats else "Locked"
                console_print(f"  {subclass_name} ({status}): {data.get('description', '')}", color="cyan")
                if status == "Locked":
                    console_print("    Requirements:", color="cyan")
                    console_print(f"      - Level: {level_req}", color="cyan")
                    for stat, value in stat_reqs.items():
                        console_print(f"      - {stat}: {value}", color="cyan")
        else:
            console_print("  None", color="cyan")
        console_print("\n=== Final Stats ===", color="cyan")
        for stat, value in stat_dict.items():
            racial_mod = combined_modifiers.get(stat, 0)
            mod_str = f" ({'+' if racial_mod >= 0 else ''}{racial_mod})" if racial_mod != 0 else ""
            console_print(f"{stat}: {value}{mod_str}", color="cyan")
        console_print("\n=== Spells ===", color="cyan")
        if spells[0] or spells[1]:
            console_print(f"Level 0: {', '.join(spells[0]) or 'None'}", color="cyan")
            console_print(f"Level 1: {', '.join(spells[1]) or 'None'}", color="cyan")
        else:
            console_print("None", color="cyan")

    def _confirm_character(self) -> str:
        console_print("\n=== Confirm Character ===", color="cyan")
        console_print("1. Change Race", color="cyan")
        console_print("2. Change Class", color="cyan")
        console_print("3. Change Spells", color="cyan")
        console_print("4. Reroll Stats", color="cyan")
        console_print("5. Confirm Character", color="cyan")
        return console_input("Select an option (1-5): ", color="yellow").strip().lower()

    def find_starting_position(self, game: Any) -> str:
        """Return a random civilization capital as the starting room."""
        logger.debug("Searching for starting capital position")
        if game.world_state.civilizations:
            civ = random.choice(game.world_state.civilizations)
            x, y = civ['capital']['x'], civ['capital']['y']
            logger.debug(f"Found capital at ({x}, {y}) for starting position")
            return f"{x},{y}"
        logger.warning("No civilizations found, defaulting to (0, 0)")
        return "0,0"