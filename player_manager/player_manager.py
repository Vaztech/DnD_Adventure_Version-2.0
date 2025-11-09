# dnd_adventure/player_manager/player_manager.py
# =============================================================================
# PlayerManager
# -----------------------------------------------------------------------------
# Responsibilities
# • Create a new Player (interactive: race → subrace → class → optional subclass
#   → stats (random/manual) → spells → confirm) OR load an existing save.
# • Read races from dnd_adventure/data/races.json with cross-platform, robust IO.
# • Provide clear, colorized CLI prompts (falls back cleanly if ANSI/color not
#   available).
# • Compute basic derived stats (HP/MP/AC/Attack) in a simple, reproducible way.
#
# Design Notes
# • Player creation is independent from worldgen/themes/graphics. That keeps
#   character flow stable regardless of where theme/graphics files live.
# • If races.json is missing/invalid/empty, we inject sane defaults so creation
#   always works.
# • This file only imports Player from your package—no circular deps.
#
# What changed vs. your last version
# • Heavier inline comments (per your request).
# • Stronger file/JSON error handling (_safe_load_json).
# • Guaranteed races.json availability (auto-writes DEFAULT_RACES if missing).
# • Friendlier prompts + graceful TTY fallbacks (try/except around color output).
# • Minor clarity/consistency tweaks; core flow preserved.
# =============================================================================

from __future__ import annotations

import json
import logging
import os
import random
from typing import Optional, Tuple, Any, Dict, List

from colorama import Fore, Style

from dnd_adventure.player import Player  # <-- no theme/graphics imports here

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Built-in minimal races (used if races.json missing/invalid/empty)
# -----------------------------------------------------------------------------
DEFAULT_RACES: List[Dict[str, Any]] = [
    {
        "name": "Human",
        "description": "Adaptable and ambitious.",
        "ability_modifiers": {},
        "subraces": {}
    },
    {
        "name": "Elf",
        "description": "Graceful and wise.",
        "ability_modifiers": {"Dexterity": 2},
        "subraces": {
            "High Elf": {
                "description": "Scholarly elves with keen minds.",
                "ability_modifiers": {"Intelligence": 1}
            },
            "Wood Elf": {
                "description": "Stealthy elves tied to forests.",
                "ability_modifiers": {"Wisdom": 1}
            }
        }
    },
    {
        "name": "Dwarf",
        "description": "Stout and hardy.",
        "ability_modifiers": {"Constitution": 2},
        "subraces": {
            "Hill Dwarf": {
                "description": "Stalwart dwarves of the hills.",
                "ability_modifiers": {"Wisdom": 1}
            },
            "Mountain Dwarf": {
                "description": "Strong dwarves of the mountains.",
                "ability_modifiers": {"Strength": 1}
            }
        }
    }
]


# -----------------------------------------------------------------------------
# Path helpers + safe JSON loader
# -----------------------------------------------------------------------------
def _pkg_root() -> str:
    """
    Resolve the absolute path to the dnd_adventure package root.

    This file lives at:
      dnd_adventure/player_manager/player_manager.py
    So the package root is one level up from this folder.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))


def _safe_load_json(path: str, default):
    """
    Load JSON with robust error handling. If file is missing or invalid,
    return the provided default so callers always get a usable object.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Missing file: {path} — using defaults.")
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {path}: {e} — using defaults.")
        return default
    except OSError as e:
        logger.error(f"OS error reading {path}: {e} — using defaults.")
        return default


# =============================================================================
# PlayerManager
# =============================================================================
class PlayerManager:
    """
    Orchestrates creating or loading a Player, including CLI menus for
    race/subrace/class/stat allocation and optional spell selection.

    Assumes `game` provides:
      • game.classes: Dict[str, Dict]  (class metadata, spellcasting info, etc.)
      • game.save_manager.load_game(save_name) -> dict or None
      • game.world.map (for picking a starting location)
    """

    def __init__(self) -> None:
        """
        Initialize the manager and load (or create) the races data.
        We target: <package_root>/data/races.json
        """
        package_root = _pkg_root()
        data_dir = os.path.join(package_root, "data")
        os.makedirs(data_dir, exist_ok=True)

        races_path = os.path.join(data_dir, "races.json")
        logger.debug(f"Loading races from {races_path}...")

        # If missing, write the defaults so the game can proceed.
        if not os.path.exists(races_path):
            logger.warning(f"races.json missing at {races_path}; writing minimal defaults.")
            try:
                with open(races_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_RACES, f, indent=2)
            except OSError as e:
                logger.error(f"Failed writing default races.json: {e}")

        # Load (never returns None thanks to _safe_load_json)
        self.races: List[Dict[str, Any]] = _safe_load_json(races_path, DEFAULT_RACES)

        # Guard: if it parsed but is empty list, restore defaults
        if not self.races:
            logger.warning("races.json loaded but empty; injecting minimal defaults.")
            self.races = DEFAULT_RACES

    # -------------------------------------------------------------------------
    # Public API: create or load player
    # -------------------------------------------------------------------------
    def initialize_player(self, game: Any, save_file: Optional[str] = None) -> Tuple[Optional[Player], Optional[str]]:
        """
        Create a new Player from interactive prompts OR load an existing one.

        Returns:
            (Player instance or None, starting_room_id as "x,y" or None)
        """
        logger.debug(f"Initializing player, save_file={save_file}")

        # Attempt load if a save file name was provided
        if save_file:
            try:
                player_data = game.save_manager.load_game(save_file)
                if player_data:
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
                    )
                    starting_room = player_data.get("current_room")
                    logger.debug(f"Loaded player: {player_data['name']}, room: {starting_room}")
                    return player, starting_room
            except Exception as e:
                logger.error(f"Failed to load save file {save_file}: {e}")
                try:
                    print(f"{Fore.RED}Failed to load save file. Starting new character.{Style.RESET_ALL}")
                except OSError:
                    print("Failed to load save file. Starting new character.")

        # Otherwise enter full creation flow
        try:
            print(f"{Fore.CYAN}Creating new character...{Style.RESET_ALL}")
        except OSError:
            print("Creating new character...")

        player_data = self._create_character(game)
        if not player_data:
            logger.error("Character creation failed or was cancelled")
            return None, None

        # Build Player object
        player = Player(
            name=getattr(game, "player_name", "Hero"),
            race=player_data["race"],
            subrace=player_data["subrace"],
            character_class=player_data["class"],
            stats=player_data["stats"],
            spells=player_data["spells"],
            level=player_data.get("level", 1),
            features=player_data["features"],
            subclass=player_data.get("subclass", None),
        )

        # Choose a starting position (first dungeon; else 0,0)
        starting_room_xy = self.find_starting_position(game)
        logger.debug("Player initialization complete")
        logger.info(
            "Character created: %s, %s, %s, %s, level %s, subclass %s",
            player.name, player.race, player.subrace, player.character_class,
            player.level, player.subclass
        )
        return player, f"{starting_room_xy[0]},{starting_room_xy[1]}"

    # -------------------------------------------------------------------------
    # Interactive creation flow (race→subrace→class→subclass→stats→spells→confirm)
    # -------------------------------------------------------------------------
    def _create_character(self, game: Any) -> Optional[Dict[str, Any]]:
        """
        Drive the interactive menus and return a data dict with the result.
        Return None if the user cancels.
        """
        logger.debug("Starting character creation")

        race: Optional[str] = None
        subrace: Optional[str] = None
        character_class: Optional[str] = None
        subclass: Optional[str] = None
        stats: Optional[List[int]] = None
        spells: Dict[int, List[str]] = {0: [], 1: []}
        features: List[str] = []
        level = 1  # starting level

        # Main creation loop—allows revisiting choices before confirmation
        while True:
            # 1) Race & Subrace ------------------------------------------------
            if not race:
                race = self._select_race()
                if not race:
                    logger.debug("Character creation cancelled during race selection")
                    return None
                subrace = self._select_subrace(race)

            # 2) Class & optional Subclass ------------------------------------
            if not character_class:
                character_class = self._select_class(game)
                if not character_class:
                    logger.debug("Character creation cancelled during class selection")
                    return None
                subclass = self._select_subclass(game, character_class, level)

            # 3) Base Stat array (random/manual) -------------------------------
            if not stats:
                stats = self._choose_stats(race, subrace, character_class)

            # 4) Compose racial/subrace modifiers for display & math -----------
            race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), {})
            subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
            race_modifiers = race_dict.get("ability_modifiers", {})
            subrace_modifiers = subrace_dict.get("ability_modifiers", {})

            combined_modifiers: Dict[str, int] = {}
            for stat, value in race_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
            for stat, value in subrace_modifiers.items():
                combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value

            # 5) Build labeled dict, then compute final list in fixed order ----
            stat_dict = {
                "Strength":      stats[0],
                "Dexterity":     stats[1],
                "Constitution":  stats[2],
                "Intelligence":  stats[3],
                "Wisdom":        stats[4],
                "Charisma":      stats[5],
            }
            for stat, value in combined_modifiers.items():
                stat_dict[stat] = stat_dict.get(stat, 6) + value

            final_stats = [
                stat_dict["Strength"],
                stat_dict["Dexterity"],
                stat_dict["Constitution"],
                stat_dict["Intelligence"],
                stat_dict["Wisdom"],
                stat_dict["Charisma"],
            ]

            # 6) Class metadata (features/spellcasting) ------------------------
            class_data = game.classes.get(character_class, {})

            # 7) Optional spell selection (only if the class can cast) ---------
            spells = {0: [], 1: []}
            if class_data.get("spellcasting"):
                spells = self._select_spells(game, character_class)

            # 8) Level-1 features (names only) ---------------------------------
            if not features:
                features = self._get_class_features(game, character_class)

            # 9) Derived stats (simple, consistent math) -----------------------
            max_hp = self._calculate_hp(class_data, stat_dict)
            current_hp = max_hp
            max_mp = self._calculate_mp(class_data, stat_dict)
            current_mp = max_mp
            attack = self._calculate_attack(class_data, stat_dict)
            defense = self._calculate_defense(stat_dict)

            # 10) Preview + Confirm menu --------------------------------------
            try:
                print(f"{Fore.CYAN}=== Character Summary ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Name: {getattr(game, 'player_name', 'Hero')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Level: {level}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Race: {race} ({subrace or 'None'}){Style.RESET_ALL}")
                print(f"{Fore.CYAN}Racial Stat Bonus: {self._format_modifiers(combined_modifiers) or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}HP: {current_hp}/{max_hp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}MP: {current_mp}/{max_mp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Attack Bonus: {attack}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}AC: {defense}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Class: {character_class}{Style.RESET_ALL}")

                print(f"\n{Fore.CYAN}=== Base Stats (before racial) ==={Style.RESET_ALL}")
                for label, value in zip(["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"], stats):
                    print(f"{Fore.CYAN}{label}: {value}{Style.RESET_ALL}")

                print(f"\n{Fore.CYAN}=== Racial/Subrace Bonuses Applied ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Race ({race}): {self._format_modifiers(race_modifiers) or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Subrace ({subrace or 'None'}): {self._format_modifiers(subrace_modifiers) or 'None'}{Style.RESET_ALL}")

                # Subclass visibility (info only)
                print(f"\n{Fore.CYAN}=== Available Subclasses at Level 1 ==={Style.RESET_ALL}")
                subclasses = class_data.get('subclasses', {})
                if subclasses:
                    for sc_name, data in subclasses.items():
                        prereqs = data.get('prerequisites', {})
                        level_req = prereqs.get('level', 1)
                        stat_reqs = prereqs.get('stats', {})
                        meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
                        status = "Unlocked" if level_req == 1 and meets_stats else "Locked"
                        print(f"{Fore.CYAN}  {sc_name} ({status}): {data.get('description', '')}{Style.RESET_ALL}")
                        if status == "Locked":
                            print(f"{Fore.CYAN}    Requirements:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}      - Level: {level_req}{Style.RESET_ALL}")
                            for s, v in stat_reqs.items():
                                print(f"{Fore.CYAN}      - {s}: {v}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}  None{Style.RESET_ALL}")

                print(f"\n{Fore.CYAN}=== Final Stats (after racial) ==={Style.RESET_ALL}")
                for k, v in stat_dict.items():
                    print(f"{Fore.CYAN}{k}: {v}{Style.RESET_ALL}")

                print(f"\n{Fore.CYAN}=== Spells ==={Style.RESET_ALL}")
                if spells[0] or spells[1]:
                    print(f"{Fore.CYAN}Level 0: {', '.join(spells[0]) or 'None'}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Level 1: {', '.join(spells[1]) or 'None'}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}None{Style.RESET_ALL}")

                print(f"\n{Fore.CYAN}=== Confirm Character ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Change Race{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Change Class{Style.RESET_ALL}")
                print(f"{Fore.CYAN}3. Change Spells{Style.RESET_ALL}")
                print(f"{Fore.CYAN}4. Reroll Stats{Style.RESET_ALL}")
                print(f"{Fore.CYAN}5. Confirm Character{Style.RESET_ALL}")
                choice = input(f"{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}").strip().lower()

            except OSError:
                # Fallback without ANSI
                print("=== Character Summary ===")
                print(f"Name: {getattr(game, 'player_name', 'Hero')}")
                print(f"Level: {level}")
                print(f"Race: {race} ({subrace or 'None'})")
                print(f"Racial Stat Bonus: {self._format_modifiers(combined_modifiers) or 'None'}")
                print(f"HP: {current_hp}/{max_hp}")
                print(f"MP: {current_mp}/{max_mp}")
                print(f"Attack Bonus: {attack}")
                print(f"AC: {defense}")
                print(f"Class: {character_class}")
                print("\n=== Base Stats (before racial) ===")
                for label, value in zip(["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"], stats):
                    print(f"{label}: {value}")
                print("\n=== Racial/Subrace Bonuses Applied ===")
                print(f"Race ({race}): {self._format_modifiers(race_modifiers) or 'None'}")
                print(f"Subrace ({subrace or 'None'}): {self._format_modifiers(subrace_modifiers) or 'None'}")
                print("\n=== Available Subclasses at Level 1 ===")
                subclasses = class_data.get('subclasses', {})
                if subclasses:
                    for sc_name, data in subclasses.items():
                        prereqs = data.get('prerequisites', {})
                        level_req = prereqs.get('level', 1)
                        stat_reqs = prereqs.get('stats', {})
                        meets_stats = all(stat_dict.get(stat, 10) >= value for stat, value in stat_reqs.items())
                        status = "Unlocked" if level_req == 1 and meets_stats else "Locked"
                        print(f"  {sc_name} ({status}): {data.get('description', '')}")
                        if status == "Locked":
                            print("    Requirements:")
                            print(f"      - Level: {level_req}")
                            for s, v in stat_reqs.items():
                                print(f"      - {s}: {v}")
                else:
                    print("  None")
                print("\n=== Final Stats (after racial) ===")
                for k, v in stat_dict.items():
                    print(f"{k}: {v}")
                print("\n=== Spells ===")
                if spells[0] or spells[1]:
                    print(f"Level 0: {', '.join(spells[0]) or 'None'}")
                    print(f"Level 1: {', '.join(spells[1]) or 'None'}")
                else:
                    print("None")
                print("\n=== Confirm Character ===")
                print("1. Change Race")
                print("2. Change Class")
                print("3. Change Spells")
                print("4. Reroll Stats")
                print("5. Confirm Character")
                choice = input("Select an option (1-5): ").strip().lower()

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
                    spells = self._select_spells(game, character_class)
                else:
                    try:
                        print(f"{Fore.RED}This class cannot cast spells.{Style.RESET_ALL}")
                    except OSError:
                        print("This class cannot cast spells.")
                continue
            elif choice == '4':
                stats = None
                continue
            elif choice == '5':
                logger.debug(
                    "Character confirmed: %s",
                    {
                        'race': race, 'subrace': subrace, 'class': character_class, 'subclass': subclass,
                        'stats': stats, 'final_stats': final_stats, 'spells': spells, 'features': features, 'level': level
                    }
                )
                return {
                    "race": race,
                    "subrace": subrace,
                    "class": character_class,
                    "subclass": subclass,
                    "stats": final_stats,
                    "stat_dict": stat_dict,
                    "spells": spells,
                    "features": features,
                    "level": level,
                }
            else:
                try:
                    print(f"{Fore.RED}Invalid choice. Please select 1-5.{Style.RESET_ALL}")
                except OSError:
                    print("Invalid choice. Please select 1-5.")

    # -------------------------------------------------------------------------
    # Simple derived-stat calculators (consistent & predictable)
    # -------------------------------------------------------------------------
    def _calculate_hp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """
        Max HP at L1 = class hit die + CON modifier (min 1).
        """
        hit_die = class_data.get("hit_die", 6)
        con_modifier = (stat_dict.get("Constitution", 10) - 10) // 2
        max_hp = hit_die + con_modifier
        return max(max_hp, 1)

    def _calculate_mp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """
        Simple MP pool for caster classes.
        """
        if not class_data.get("spellcasting"):
            return 0
        primary_stat = class_data.get("spellcasting_stat", "Intelligence")
        stat_modifier = (stat_dict.get(primary_stat, 10) - 10) // 2
        return max(2 + stat_modifier, 0)

    def _calculate_attack(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        """
        Attack bonus = (very rough BAB by progression) + better of STR/DEX mod.
        """
        bab = 0
        prog = class_data.get("bab_progression")
        if prog == "fast":
            bab = 1
        elif prog == "medium":
            bab = 0
        # 'slow' or unspecified -> 0 at level 1
        dex_mod = (stat_dict.get("Dexterity", 10) - 10) // 2
        str_mod = (stat_dict.get("Strength", 10) - 10) // 2
        return max(bab + max(dex_mod, str_mod), 0)

    def _calculate_defense(self, stat_dict: Dict[str, int]) -> int:
        """
        AC = 10 + DEX modifier (no armor system yet).
        """
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        return 10 + dex_modifier

    # -------------------------------------------------------------------------
    # Subclass selection (unlocked at L1 only if requirements met)
    # -------------------------------------------------------------------------
    def _select_subclass(self, game: Any, character_class: str, level: int) -> Optional[str]:
        logger.debug(f"Selecting subclass for {character_class}")
        class_data = game.classes.get(character_class, {})
        subclasses = class_data.get("subclasses", {})
        if not subclasses:
            logger.debug(f"No subclasses available for {character_class}")
            return None

        unlocked: List[Tuple[str, Dict[str, Any]]] = []
        for subclass_name, data in subclasses.items():
            prereqs = data.get("prerequisites", {})
            level_req = prereqs.get("level", 1)
            if level >= level_req:
                unlocked.append((subclass_name, data))

        if not unlocked:
            logger.debug(f"No unlocked subclasses for {character_class} at level {level}")
            return None

        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Subclass (or None) ==={Style.RESET_ALL}")
                for i, (sc_name, data) in enumerate(unlocked, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {sc_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {data.get('description', '')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{len(unlocked) + 1}. None{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select subclass (1-{len(unlocked)+1}): {Style.RESET_ALL}").strip()
            except OSError:
                print("=== Select Your Subclass (or None) ===")
                for i, (sc_name, data) in enumerate(unlocked, 1):
                    print("----------------------------------------")
                    print(f"{i}. {sc_name}")
                    print(f"     {data.get('description', '')}")
                print("----------------------------------------")
                print(f"{len(unlocked)+1}. None")
                selection = input(f"Select subclass (1-{len(unlocked)+1}): ").strip()

            logger.debug(f"Selected subclass: {selection}")
            if selection.isdigit():
                idx = int(selection) - 1
                if 0 <= idx < len(unlocked):
                    return unlocked[idx][0]
                elif idx == len(unlocked):
                    return None

            try:
                print(f"{Fore.RED}Invalid selection. Please enter a number (1-{len(unlocked)+1}).{Style.RESET_ALL}")
            except OSError:
                print(f"Invalid selection. Please enter a number (1-{len(unlocked)+1}).")

    # -------------------------------------------------------------------------
    # Stat allocation (menu) → random or manual point-buy
    # -------------------------------------------------------------------------
    def _choose_stats(self, race: str, subrace: Optional[str], character_class: str) -> List[int]:
        """
        Choose how to generate the six stats:
        • Random allocation: 30-point weighted buy (1..12 pre-mods)
        • Manual allocation: 25-point buy (start at 6, 4..15 pre-mods)
        """
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Stat Allocation Method ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}1. Random Allocation{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     Randomly allocate 30 points (min 1, max 12 before modifiers).{Style.RESET_ALL}")
                print(f"{Fore.CYAN}2. Allocate Points Manually{Style.RESET_ALL}")
                print(f"{Fore.CYAN}     Distribute 25 points (start at 6, min 4, max 15 before modifiers).{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                choice = input(f"{Fore.YELLOW}Select method (1-2): {Style.RESET_ALL}").strip()
            except OSError:
                print("=== Select Stat Allocation Method ===")
                print("1. Random Allocation")
                print("     Randomly allocate 30 points (min 1, max 12 before modifiers).")
                print("2. Allocate Points Manually")
                print("     Distribute 25 points (start at 6, min 4, max 15 before modifiers).")
                print("----------------------------------------")
                choice = input("Select method (1-2): ").strip()

            logger.debug(f"Selected stat method: {choice}")
            if choice == "1":
                # Repeatedly roll a weighted array until the player accepts
                while True:
                    stats = self._allocate_stats(race, subrace, character_class, point_pool=30, random_allocation=True)
                    try:
                        print(f"{Fore.CYAN}Generated Stats:{Style.RESET_ALL}")
                        for stat, value in zip(
                            ["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"], stats
                        ):
                            print(f"{Fore.CYAN}{stat}: {value}{Style.RESET_ALL}")
                        accept = input(f"{Fore.YELLOW}Accept stats? (yes/no): {Style.RESET_ALL}").strip().lower()
                    except OSError:
                        print("Generated Stats:")
                        for stat, value in zip(
                            ["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"], stats
                        ):
                            print(f"{stat}: {value}")
                        accept = input("Accept stats? (yes/no): ").strip().lower()

                    if accept == "yes":
                        return stats
                    elif accept != "no":
                        try:
                            print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                        except OSError:
                            print("Please enter 'yes' or 'no'.")

            elif choice == "2":
                # Manual point-buy
                return self._allocate_stats(race, subrace, character_class, point_pool=25, random_allocation=False)

            else:
                try:
                    print(f"{Fore.RED}Invalid choice. Please select 1 or 2.{Style.RESET_ALL}")
                except OSError:
                    print("Invalid choice. Please select 1 or 2.")

    # -------------------------------------------------------------------------
    # Shared allocator used by random/manual modes (weighted costs)
    # -------------------------------------------------------------------------
    def _allocate_stats(
        self,
        race: str,
        subrace: Optional[str],
        character_class: str,
        point_pool: int,
        random_allocation: bool
    ) -> List[int]:
        """
        Flexible point-buy with tiered costs. In random mode, we bias toward
        viable mid-range arrays and give the class’ primary stat a floor.
        """
        # Tiered cost map (credits for <6, escalating cost >12)
        point_buy_costs = {
            1: -5, 2: -4, 3: -3,
            4: -2, 5: -1,
            6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6,
            13: 8, 14: 10, 15: 12,
            16: 15, 17: 18, 18: 21
        }

        # Bounds differ by mode
        min_stat = 1 if random_allocation else 4
        max_stat = 12 if random_allocation else 15
        base_stat = 1 if random_allocation else 6
        stats = [base_stat] * 6

        # Compute combined racial modifiers (for UI)
        race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), {})
        subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
        race_modifiers = race_dict.get("ability_modifiers", {})
        subrace_modifiers = subrace_dict.get("ability_modifiers", {})

        combined_modifiers: Dict[str, int] = {}
        for stat, value in race_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
        for stat, value in subrace_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value

        # Class primary stat preference
        preferred_stats = {
            "Barbarian": "Strength",
            "Bard": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Fighter": "Strength",
            "Monk": "Dexterity",
            "Paladin": "Charisma",
            "Ranger": "Dexterity",
            "Rogue": "Dexterity",
            "Sorcerer": "Charisma",
            "Wizard": "Intelligence",
            "Assassin": "Dexterity",
        }
        stat_names = ["Strength","Dexterity","Constitution","Intelligence","Wisdom","Charisma"]
        preferred_stat = preferred_stats.get(character_class, "Intelligence")
        preferred_idx = stat_names.index(preferred_stat)

        if random_allocation:
            # Weighted random fill with a decent floor for the primary stat
            unallocated_points = point_pool

            preferred_value = min(12, max(10, random.randint(8, 12)))
            stats[preferred_idx] = preferred_value
            unallocated_points -= (point_buy_costs[preferred_value] - point_buy_costs[base_stat])

            possible_values = [v for v in point_buy_costs if min_stat <= v <= max_stat]
            weights = [1 if v < 8 else 3 for v in possible_values]  # bias toward 8–12

            while unallocated_points > 0:
                idx = random.randint(0, 5)
                if stats[idx] >= max_stat:
                    continue
                # Find increases that fit remaining budget
                next_values = [
                    v for v in possible_values
                    if v > stats[idx] and (point_buy_costs[v] - point_buy_costs[stats[idx]]) <= unallocated_points
                ]
                if not next_values:
                    continue
                # Map weights to the subset length
                local_weights = weights[:len(next_values)]
                new_val = random.choices(next_values, weights=local_weights, k=1)[0]
                delta = point_buy_costs[new_val] - point_buy_costs[stats[idx]]
                stats[idx] = new_val
                unallocated_points -= delta

            logger.debug(f"Randomly allocated stats: {stats}")
            return stats

        # -------- Manual point-buy UI ----------------------------------------
        unallocated_points = point_pool

        def cost_to_increment(current: int) -> Optional[int]:
            if current >= max_stat:
                return None
            nxt = current + 1
            return point_buy_costs.get(nxt, float('inf')) - point_buy_costs.get(current, 0)

        descriptions = [
            "Affects melee attack/damage, carry capacity.",
            "Affects AC, ranged attacks, Reflex/stealth.",
            "Affects HP, Fortitude, endurance.",
            "Affects Wizard spells, skill points, knowledge.",
            "Affects Cleric/Druid spells, Will, perception.",
            "Affects Sorcerer/Bard spells, social, leadership.",
        ]

        while True:
            try:
                print(f"{Fore.CYAN}=== Manual Stat Allocation ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Unallocated points: {unallocated_points}{Style.RESET_ALL}")
                for i, (name, value, desc) in enumerate(zip(stat_names, stats, descriptions), 1):
                    mod = (value + combined_modifiers.get(name, 0) - 10) // 2
                    c = cost_to_increment(value)
                    c_str = f"To increase to {value+1}: {c} points" if c is not None else "Maxed out"
                    print(f"{Fore.CYAN}{i}. {name}: {value} ({'+' if mod >= 0 else ''}{mod}){Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {desc}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {c_str}{Style.RESET_ALL}")
                selection = input(f"{Fore.YELLOW}Select stat (1-6) or 'done' to finalize: {Style.RESET_ALL}").strip().lower()
            except OSError:
                print("=== Manual Stat Allocation ===")
                print(f"Unallocated points: {unallocated_points}")
                for i, (name, value, desc) in enumerate(zip(stat_names, stats, descriptions), 1):
                    mod = (value + combined_modifiers.get(name, 0) - 10) // 2
                    c = cost_to_increment(value)
                    c_str = f"To increase to {value+1}: {c} points" if c is not None else "Maxed out"
                    print(f"{i}. {name}: {value} ({'+' if mod >= 0 else ''}{mod})")
                    print(f"     {desc}")
                    print(f"     {c_str}")
                selection = input("Select stat (1-6) or 'done' to finalize: ").strip().lower()

            if selection == "done":
                if unallocated_points > 0:
                    try:
                        print(f"{Fore.RED}You still have {unallocated_points} points unallocated.{Style.RESET_ALL}")
                        finalize = input(f"{Fore.YELLOW}Finalize anyway? (yes/no): {Style.RESET_ALL}").strip().lower()
                    except OSError:
                        print(f"You still have {unallocated_points} points unallocated.")
                        finalize = input("Finalize anyway? (yes/no): ").strip().lower()
                    if finalize == "yes":
                        logger.debug(f"Finalized stats: {stats} (unused points: {unallocated_points})")
                        return stats
                    elif finalize != "no":
                        try:
                            print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                        except OSError:
                            print("Please enter 'yes' or 'no'.")
                    continue
                try:
                    finalize = input(f"{Fore.YELLOW}Finalize stats? (yes/no): {Style.RESET_ALL}").strip().lower()
                except OSError:
                    finalize = input("Finalize stats? (yes/no): ").strip().lower()
                if finalize == "yes":
                    logger.debug(f"Finalized stats: {stats}")
                    return stats
                elif finalize != "no":
                    try:
                        print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
                    except OSError:
                        print("Please enter 'yes' or 'no'.")
                continue

            if not selection.isdigit() or not 1 <= int(selection) <= 6:
                try:
                    print(f"{Fore.RED}Invalid input. Select a number (1-6) or 'done'.{Style.RESET_ALL}")
                except OSError:
                    print("Invalid input. Select a number (1-6) or 'done'.")
                continue

            idx = int(selection) - 1
            try:
                prompt = (
                    f"{Fore.YELLOW}Enter target value for {stat_names[idx]} ({min_stat}-{max_stat}) "
                    f"or '+n'/'-n' to adjust (e.g., '+2', '-1'): {Style.RESET_ALL}"
                )
                raw = input(prompt).strip()

                if raw.startswith(("+", "-")):
                    delta = int(raw)
                    target = stats[idx] + delta
                else:
                    target = int(raw)

                if target < min_stat or target > max_stat:
                    try:
                        print(f"{Fore.RED}Value must be between {min_stat} and {max_stat}.{Style.RESET_ALL}")
                    except OSError:
                        print(f"Value must be between {min_stat} and {max_stat}.")
                    continue

                cost_new = point_buy_costs.get(target, float('inf'))
                cost_old = point_buy_costs.get(stats[idx], 0)
                delta_cost = cost_new - cost_old

                if delta_cost > unallocated_points:
                    try:
                        print(f"{Fore.RED}Not enough points ({unallocated_points} available, need {delta_cost}).{Style.RESET_ALL}")
                    except OSError:
                        print(f"Not enough points ({unallocated_points} available, need {delta_cost}).")
                    continue

                if delta_cost < 0 and abs(delta_cost) > point_pool - unallocated_points:
                    # Prevent “refund” exploits beyond originally allocated total
                    try:
                        print(f"{Fore.RED}Cannot remove more points than allocated.{Style.RESET_ALL}")
                    except OSError:
                        print("Cannot remove more points than allocated.")
                    continue

                stats[idx] = target
                unallocated_points -= delta_cost
                logger.debug(f"Updated {stat_names[idx]} to {stats[idx]}, unallocated: {unallocated_points}")

            except ValueError:
                try:
                    print(f"{Fore.RED}Invalid input. Enter {min_stat}-{max_stat} or '+n'/'-n'.{Style.RESET_ALL}")
                except OSError:
                    print(f"Invalid input. Enter {min_stat}-{max_stat} or '+n'/'-n'.")

    # -------------------------------------------------------------------------
    # Render helper for "STR: +2, DEX: -1" style strings
    # -------------------------------------------------------------------------
    def _format_modifiers(self, modifiers: Dict[str, int]) -> str:
        return ", ".join(f"{k}: {'+' if v > 0 else ''}{v}" for k, v in modifiers.items()) if modifiers else ""

    # -------------------------------------------------------------------------
    # Race / Subrace menus (data driven from races.json or DEFAULT_RACES)
    # -------------------------------------------------------------------------
    def _select_race(self) -> Optional[str]:
        """
        Display the race list and return the chosen race name.
        Thanks to defaults, this is never an empty list.
        """
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Race ==={Style.RESET_ALL}")
                for i, race in enumerate(self.races, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {race['name']}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {race.get('description', '')}{Style.RESET_ALL}")
                    mods = race.get("ability_modifiers", {})
                    mod_str = self._format_modifiers(mods)
                    print(f"{Fore.CYAN}     Stat Modifiers: {mod_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                sel = input(f"{Fore.YELLOW}Select race (1-{len(self.races)}): {Style.RESET_ALL}").strip()
            except OSError:
                print("=== Select Your Race ===")
                for i, race in enumerate(self.races, 1):
                    print("----------------------------------------")
                    print(f"{i}. {race['name']}")
                    print(f"     {race.get('description', '')}")
                    mods = race.get("ability_modifiers", {})
                    mod_str = self._format_modifiers(mods)
                    print(f"     Stat Modifiers: {mod_str or 'None'}")
                print("----------------------------------------")
                sel = input(f"Select race (1-{len(self.races)}): ").strip()

            logger.debug(f"Selected race: {sel}")
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(self.races):
                    return self.races[idx]["name"]

            try:
                print(f"{Fore.RED}Invalid race. Enter a number (1-{len(self.races)}).{Style.RESET_ALL}")
            except OSError:
                print(f"Invalid race. Enter a number (1-{len(self.races)}).")

    def _select_subrace(self, race: str) -> Optional[str]:
        """
        If the chosen race has subraces, present them; otherwise return None.
        """
        race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), None)
        subraces = race_dict.get("subraces", {}) if race_dict else {}
        if not subraces:
            return None

        items = list(subraces.items())
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Subrace ==={Style.RESET_ALL}")
                for i, (sub_name, sub_data) in enumerate(items, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {sub_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {sub_data.get('description', '')}{Style.RESET_ALL}")
                    mods = sub_data.get("ability_modifiers", {})
                    mod_str = self._format_modifiers(mods)
                    print(f"{Fore.CYAN}     Stat Modifiers: {mod_str or 'None'}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                sel = input(f"{Fore.YELLOW}Select subrace (1-{len(items)}): {Style.RESET_ALL}").strip()
            except OSError:
                print("=== Select Your Subrace ===")
                for i, (sub_name, sub_data) in enumerate(items, 1):
                    print("----------------------------------------")
                    print(f"{i}. {sub_name}")
                    print(f"     {sub_data.get('description', '')}")
                    mods = sub_data.get("ability_modifiers", {})
                    mod_str = self._format_modifiers(mods)
                    print(f"     Stat Modifiers: {mod_str or 'None'}")
                print("----------------------------------------")
                sel = input(f"Select subrace (1-{len(items)}): ").strip()

            logger.debug(f"Selected subrace: {sel}")
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(items):
                    return items[idx][0]

            try:
                print(f"{Fore.RED}Invalid subrace. Enter a number (1-{len(items)}).{Style.RESET_ALL}")
            except OSError:
                print(f"Invalid subrace. Enter a number (1-{len(items)}).")

    # -------------------------------------------------------------------------
    # Class selection (data from game.classes)
    # -------------------------------------------------------------------------
    def _select_class(self, game: Any) -> Optional[str]:
        """
        Show available classes (from game.classes) and return the chosen one.
        """
        logger.debug("Starting class selection")
        classes = game.classes

        preferred = {
            "Barbarian": "Strength",
            "Bard": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Fighter": "Strength",
            "Monk": "Dexterity",
            "Paladin": "Charisma",
            "Ranger": "Dexterity",
            "Rogue": "Dexterity",
            "Sorcerer": "Charisma",
            "Wizard": "Intelligence",
            "Assassin": "Dexterity",
        }

        items = list(classes.items())
        while True:
            try:
                print(f"{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
                for i, (name, data) in enumerate(items, 1):
                    print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{i}. {name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     {data.get('description', '')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Preferred Stat: {preferred.get(name, 'Unknown')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
                sel = input(f"{Fore.YELLOW}Select class (1-{len(items)}): {Style.RESET_ALL}").strip()
            except OSError:
                print("=== Select Your Class ===")
                for i, (name, data) in enumerate(items, 1):
                    print("----------------------------------------")
                    print(f"{i}. {name}")
                    print(f"     {data.get('description', '')}")
                    print(f"     Preferred Stat: {preferred.get(name, 'Unknown')}")
                print("----------------------------------------")
                sel = input(f"Select class (1-{len(items)}): ").strip()

            logger.debug(f"Selected class: {sel}")
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(items):
                    return items[idx][0]

            try:
                print(f"{Fore.RED}Invalid class. Enter a number (1-{len(items)}).{Style.RESET_ALL}")
            except OSError:
                print(f"Invalid class. Enter a number (1-{len(items)}).")

    # -------------------------------------------------------------------------
    # Spell selection (optional; driven by class metadata or spells.json)
    # -------------------------------------------------------------------------
    def _select_spells(self, game: Any, character_class: str) -> Dict[int, List[str]]:
        """
        Select level-0 (cantrips) and level-1 spells if the class can cast.
        Prefers dnd_adventure/data/spells.json if present; otherwise a small
        built-in pool.
        """
        classes = game.classes
        class_data = classes.get(character_class, {})
        spells: Dict[int, List[str]] = {0: [], 1: []}

        if not class_data.get("spellcasting"):
            logger.debug(f"No spells for non-spellcasting class: {character_class}")
            return spells

        # Try external spells.json
        package_root = _pkg_root()
        data_dir = os.path.join(package_root, "data")
        spells_path = os.path.join(data_dir, "spells.json")
        external = _safe_load_json(spells_path, {})

        # Minimal built-ins if external is missing or empty for this class
        default_spells = {
            "Assassin": {
                "0": [],
                "1": [
                    {"name": "Disguise Self", "description": "Change your appearance.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Silent Image", "description": "Create an illusion.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Ghost Sound", "description": "Minor sounds or music.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                ],
            },
            "Wizard": {
                "0": [
                    {"name": "Prestidigitation", "description": "Minor tricks.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Mage Hand", "description": "Move 5 lb. at range.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Detect Magic", "description": "Sense magic.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                    {"name": "Light", "description": "Object glows.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0},
                ],
                "1": [
                    {"name": "Magic Missile", "description": "Auto-hit force darts.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Shield", "description": "+4 AC; block missiles.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Charm Person", "description": "Turns target friendly.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                    {"name": "Burning Hands", "description": "Close cone fire.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1},
                ],
            },
            "Cleric": {
                "0": [
                    {"name": "Guidance", "description": "+1 to next roll.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Light", "description": "Object glows.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Detect Magic", "description": "Sense magic.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                    {"name": "Create Water", "description": "Conjure clean water.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0},
                ],
                "1": [
                    {"name": "Bless", "description": "+1 attacks; vs fear.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Cure Light Wounds", "description": "Heal 1d8+1/level.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Shield of Faith", "description": "+2 deflection.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                    {"name": "Command", "description": "1-round compulsion.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1},
                ],
            },
        }

        available = external.get(character_class, default_spells.get(character_class, {}))
        if not available:
            logger.warning(f"No spells defined for {character_class} in spells.json or defaults")
            try:
                print(f"{Fore.YELLOW}No spells available for {character_class} at level 1.{Style.RESET_ALL}")
            except OSError:
                print(f"No spells available for {character_class} at level 1.")
            return spells

        for lvl in [0, 1]:
            level_spells = available.get(str(lvl), [])
            if not level_spells:
                continue

            max_spells = 4 if lvl == 0 else 2
            try:
                print(f"{Fore.CYAN}=== Select Level {lvl} Spells (Choose up to {max_spells}) ==={Style.RESET_ALL}")
                for i, spell in enumerate(level_spells, 1):
                    nm = spell if isinstance(spell, str) else spell.get("name", "Unknown")
                    desc = spell.get("description", "No description") if isinstance(spell, dict) else "No description"
                    mp = spell.get("mp_cost", "Unknown") if isinstance(spell, dict) else "Unknown"
                    print(f"{Fore.CYAN}{i}. {nm}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     Description: {desc}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}     MP Cost: {mp}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}----------------------------------------{Style.RESET_ALL}")
            except OSError:
                print(f"=== Select Level {lvl} Spells (Choose up to {max_spells}) ===")
                for i, spell in enumerate(level_spells, 1):
                    nm = spell if isinstance(spell, str) else spell.get("name", "Unknown")
                    desc = spell.get("description", "No description") if isinstance(spell, dict) else "No description"
                    mp = spell.get("mp_cost", "Unknown") if isinstance(spell, dict) else "Unknown"
                    print(f"{i}. {nm}")
                    print(f"     Description: {desc}")
                    print(f"     MP Cost: {mp}")
                print("----------------------------------------")

            selected: List[str] = []
            while len(selected) < max_spells:
                try:
                    choice = input(
                        f"{Fore.YELLOW}Select spell {len(selected)+1}/{max_spells} (number, name, or 'done'): {Style.RESET_ALL}"
                    ).strip().lower()
                except OSError:
                    choice = input(
                        f"Select spell {len(selected)+1}/{max_spells} (number, name, or 'done'): "
                    ).strip().lower()

                if choice == 'done' and selected:
                    break

                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(level_spells):
                        nm = level_spells[idx]["name"] if isinstance(level_spells[idx], dict) else level_spells[idx]
                        if nm not in selected:
                            selected.append(nm)
                            logger.debug(f"Selected spell: {nm}")
                        else:
                            try:
                                print(f"{Fore.RED}Spell already selected. Try again.{Style.RESET_ALL}")
                            except OSError:
                                print("Spell already selected. Try again.")
                    else:
                        try:
                            print(f"{Fore.RED}Invalid number. Try again.{Style.RESET_ALL}")
                        except OSError:
                            print("Invalid number. Try again.")
                else:
                    # name match (case-insensitive)
                    for spell in level_spells:
                        nm = spell["name"] if isinstance(spell, dict) else spell
                        if nm.lower() == choice and nm not in selected:
                            selected.append(nm)
                            logger.debug(f"Selected spell: {nm}")
                            break
                    else:
                        try:
                            print(f"{Fore.RED}Invalid or already selected spell. Try again.{Style.RESET_ALL}")
                        except OSError:
                            print("Invalid or already selected spell. Try again.")

            spells[lvl] = selected
            logger.debug(f"Selected spells for level {lvl}: {selected}")

        return spells

    # -------------------------------------------------------------------------
    # Level-1 features
    # -------------------------------------------------------------------------
    def _get_class_features(self, game: Any, character_class: str) -> List[str]:
        classes = game.classes
        class_data = classes.get(character_class, {})
        feats = [f["name"] for f in class_data.get("features", []) if f.get("level", 1) == 1]
        logger.debug(f"Selected features for {character_class}: {feats}")
        return feats

     # -------------------------------------------------------------------------
    # Choose a starting room that actually exists
    # -------------------------------------------------------------------------
    def find_starting_position(self, game: Any) -> Tuple[int, int]:
        """
        Returns a valid starting position guaranteed to exist in the world.
        Uses GameWorld.starting_room_id or raises if unavailable.
        """
        game_world = getattr(game, "game_world", None)

        if game_world and hasattr(game_world, "starting_room_id"):
            room_id = game_world.starting_room_id
            try:
                x, y = map(int, room_id.split(","))
                return x, y
            except Exception as e:
                logger.error(f"Invalid starting_room_id format: '{room_id}': {e}")
                raise RuntimeError("Corrupted starting_room_id in GameWorld.")

        raise RuntimeError("No starting room defined. World generation may have failed.")

        """
        This prevents "No room found for ID 0,0!" by ensuring we only return
        coordinates that correspond to something that actually exists whenever
        possible.
        """
        logger.debug("Searching for a valid starting position")

        # --- 1. Prefer concrete rooms from GameWorld ---------------------------------
        game_world = getattr(game, "game_world", None)
        if game_world is not None and hasattr(game_world, "rooms"):
            rooms = game_world.rooms

            if isinstance(rooms, dict) and rooms:
                logger.debug(f"GameWorld has {len(rooms)} rooms; looking for a dungeon to start in")

                dungeon_room_id = None
                fallback_room_id = None

                for room_id, room in rooms.items():
                    # room_id is expected to look like "x,y"
                    if fallback_room_id is None:
                        fallback_room_id = room_id

                    # Try to detect "dungeon" type robustly:
                    rtype = getattr(room, "room_type", None)
                    rtype_name = getattr(rtype, "name", "").lower() if rtype else ""
                    if "dungeon" in rtype_name:
                        dungeon_room_id = room_id
                        break

                chosen_id = dungeon_room_id or fallback_room_id
                if chosen_id:
                    try:
                        x_str, y_str = chosen_id.split(",")
                        x, y = int(x_str), int(y_str)
                        logger.debug(f"Starting in GameWorld room {chosen_id} -> ({x}, {y})")
                        return x, y
                    except Exception as e:
                        logger.error(f"Invalid room_id format '{chosen_id}' in GameWorld.rooms: {e}")

        # --- 2. Fallback: use locations from procedural world map --------------------
        locations = getattr(getattr(game, "world", None), "map", {}).get("locations", {})

        # Dict-based: { "x,y": { "type": "...", ... }, ... }
        if isinstance(locations, dict) and locations:
            logger.debug(f"Using dict-based locations ({len(locations)} entries)")

            # Prefer a dungeon location
            for key, loc in locations.items():
                if isinstance(loc, dict) and loc.get("type") == "dungeon":
                    try:
                        x, y = map(int, key.split(","))
                        logger.debug(f"Starting at dungeon location {key} -> ({x}, {y})")
                        return x, y
                    except Exception as e:
                        logger.error(f"Bad location key '{key}' in locations: {e}")

            # Otherwise: first valid location
            first_key = next(iter(locations.keys()))
            try:
                x, y = map(int, first_key.split(","))
                logger.debug(f"No dungeon found; starting at first location {first_key} -> ({x}, {y})")
                return x, y
            except Exception as e:
                logger.error(f"Bad first location key '{first_key}' in locations: {e}")

        # List-based: [ { "x": ..., "y": ..., "type": ... }, ... ]
        if isinstance(locations, list) and locations:
            logger.debug(f"Using list-based locations ({len(locations)} entries)")

            # Prefer dungeon
            for loc in locations:
                if isinstance(loc, dict) and loc.get("type") == "dungeon":
                    x = int(loc.get("x", 0))
                    y = int(loc.get("y", 0))
                    logger.debug(f"Starting at dungeon location ({x}, {y}) [list-based]")
                    return x, y

            # Otherwise: first entry
            first = locations[0]
            if isinstance(first, dict):
                x = int(first.get("x", 0))
                y = int(first.get("y", 0))
                logger.debug(f"No dungeon found; starting at first list location ({x}, {y})")
                return x, y

        # --- 3. Absolute last resort -------------------------------------------------
        logger.warning(
            "No suitable starting room/location found; defaulting to (0, 0). "
            "If you still see 'No room found for ID 0,0', ensure GameWorld generates rooms "
            "and that world/map_generator are wired correctly."
        )
        return (0, 0)
