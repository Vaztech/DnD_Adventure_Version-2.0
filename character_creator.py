# dnd_adventure/character_creator.py
# ------------------------------------------------------------
# Purpose:
#   Console-driven character creation flow that:
#     1) Lets the player pick Race (and optional Subrace)
#     2) Lets the player pick Class (and Cleric Domain if applicable)
#     3) Rolls/allocates stats via stat_roller.roll_stats(...)
#     4) Chooses starting spells via spell_selector.select_spells(...)
#     5) Reviews the build and returns a Character object
#
# Notes:
#   - We keep your existing selectors (race/class/spells/review).
#   - We convert game.races (dicts) into Race dataclass instances safely.
#   - We add robust error handling and user-friendly prompts.
#   - We fix a bug: modifiers_str could be referenced before assignment for "Base ..." entries.
#   - Graphics/json path changes are handled elsewhere; this file does not read graphics.json.
# ------------------------------------------------------------

import os
from typing import Dict, List, Optional
import logging
from colorama import Fore, Style

from dnd_adventure.race_selector import select_race
from dnd_adventure.class_selector import select_class
from dnd_adventure.stat_roller import roll_stats   # Your existing stats logic (manual/random) lives here
from dnd_adventure.spell_selector import select_spells
from dnd_adventure.selection_reviewer import review_selections

from dnd_adventure.character import Character
from dnd_adventure.race_models import Race  # Dataclass/model for races

logger = logging.getLogger(__name__)


def _clear_screen() -> None:
    """Cross-platform terminal clear to keep the UI readable."""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        # Not fatal; if clear fails, continue without it.
        pass


def _select_subrace_for_race(selected_race: Race, race_name: str) -> Optional[str]:
    """
    Render a subrace selection menu if the chosen race defines subraces.
    Returns:
        - The selected subrace name (string), or
        - "Base <RaceName>" if player picks the base variant, or
        - None if race has no subraces.
    Raises:
        SystemExit (graceful), if the player quits at this step.
    """
    # If the race has no subraces at all, skip menu.
    if not selected_race or not selected_race.subraces:
        return None

    # Build display list -> ['High Elf', 'Wood Elf', 'Base Elf']
    subrace_names = list(selected_race.subraces.keys()) + [f"Base {race_name}"]

    while True:
        _clear_screen()
        print(f"\n{Fore.CYAN}=== Select Your Subrace ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")

        # Render each subrace choice with a one-line description and modifiers summary.
        for i, subrace in enumerate(subrace_names, 1):
            if subrace.startswith("Base "):
                # Base variant: describe plainly and show no additional modifiers.
                desc = f"Standard {race_name} with no subrace-specific traits."
                modifiers_str = "No additional modifiers"
            else:
                # Pull subrace data and show a trimmed description + bonuses.
                subrace_data: Dict = selected_race.subraces.get(subrace, {})
                raw_desc = subrace_data.get("description", "No description available")
                desc = (raw_desc[:100] + "...") if len(raw_desc) > 100 else raw_desc
                modifiers: Dict[str, int] = subrace_data.get("stat_bonuses", {})
                # Produce a clean "STR:+2, DEX:+1" style list, or a friendly fallback.
                modifiers_str = ", ".join(f"{k}: {v:+d}" for k, v in modifiers.items()) or "No additional modifiers"

            print(f"{Fore.YELLOW}{i}. {subrace}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}Modifiers: {modifiers_str}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")

        # Accept numeric selection or 'q' to quit back to main menu.
        try:
            choice = input(f"\n{Fore.CYAN}Enter number (or 'q' to quit): {Style.RESET_ALL}").strip().lower()
            if choice == 'q':
                logger.info("Game exited during subrace selection")
                raise SystemExit("Subrace selection cancelled")
            idx = int(choice) - 1
            if 0 <= idx < len(subrace_names):
                return subrace_names[idx]
            else:
                print(f"{Fore.RED}Invalid choice. Please select a number between 1 and {len(subrace_names)}.{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number or 'q'.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def _select_cleric_domain_if_needed(class_name: str) -> Optional[str]:
    """
    If the chosen class is Cleric, guide the player to pick a domain.
    Returns the chosen domain or None for non-Clerics.
    Raises:
        SystemExit (graceful), if the player quits at this step.
    """
    if class_name != "Cleric":
        return None

    # You can expand this list or load it from JSON if desired.
    domains = ["Air", "Death", "Healing", "War"]

    while True:
        _clear_screen()
        print(f"\n{Fore.CYAN}=== Select a Cleric Domain ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")

        for i, domain in enumerate(domains, 1):
            # Lightweight flavor text for clarity.
            desc = {
                "Air": "Masters of wind and storms, wielding tempestuous magic.",
                "Death": "Commanders of necromantic energies and the undead.",
                "Healing": "Restorers of life and vitality through divine power.",
                "War": "Champions of battle, blessed with martial prowess."
            }.get(domain, "No description available")
            print(f"{Fore.YELLOW}{i}. {domain}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")

        try:
            choice = input(f"\n{Fore.CYAN}Enter number (or 'q' to quit): {Style.RESET_ALL}").strip().lower()
            if choice == 'q':
                logger.info("Game exited during domain selection")
                raise SystemExit("Domain selection cancelled")
            idx = int(choice) - 1
            if 0 <= idx < len(domains):
                domain = domains[idx]
                logger.debug(f"Selected domain: {domain}")
                return domain
            else:
                print(f"{Fore.RED}Invalid choice. Please select a number between 1 and {len(domains)}.{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number or 'q'.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def create_player(name: str, game: object) -> Optional['Character']:
    """
    Main entry point called by your game loop to build a Character.

    Args:
        name: The character's name (already captured from the player).
        game: A game-like object exposing:
              - game.races (list[dict|Race])
              - game.classes (dict[str, Any])
              - any additional context needed by stat_roller / spell selector.

    Returns:
        Character instance if confirmed by player, otherwise None.
    """
    logger.debug("Creating new player")

    # ---------------------------
    # 1) Normalize the races list
    # ---------------------------
    # Accept both dicts and Race instances; convert dicts to Race so downstream code is consistent.
    raw_races = getattr(game, "races", None)
    if not raw_races:
        logger.error("No races available in the current game context.")
        print(f"{Fore.RED}Error: No races are defined. Please check your data files.{Style.RESET_ALL}")
        return None

    races: List[Race] = [Race(**r) if isinstance(r, dict) else r for r in raw_races]

    # ---------------------------
    # 2) Read classes dictionary
    # ---------------------------
    classes: Dict = getattr(game, "classes", None)
    if not classes:
        logger.error("No classes available in the current game context.")
        print(f"{Fore.RED}Error: No classes are defined. Please check your data files.{Style.RESET_ALL}")
        return None

    # This dictionary accumulates the user's choices and computed outputs.
    selections: Dict[str, Optional[object]] = {
        "race": None,
        "subrace": None,
        "class": None,
        "stats": None,
        "stat_dict": None,
        "spells": None,
        "domain": None
    }

    try:
        # ---------------------------
        # 3) Race selection (menu)
        # ---------------------------
        selections["race"] = select_race(races)
        selected_race: Optional[Race] = next((r for r in races if r.name == selections["race"]), None)
        if not selected_race:
            logger.error(f"Selected race '{selections['race']}' not found in game.races")
            print(f"{Fore.RED}Error: Selected race not found. Please check your data files.{Style.RESET_ALL}")
            return None

        # ---------------------------
        # 4) Optional subrace menu
        # ---------------------------
        # If the race has subraces, prompt. Returns e.g. "High Elf" or "Base Elf".
        selections["subrace"] = _select_subrace_for_race(selected_race, selections["race"])

        # If player picked "Base Race", let downstream logic treat it as no subrace;
        # your stat_roller handles both [{"race": base}, {"race": base, "subrace": name}]
        if selections["subrace"] and selections["subrace"].startswith("Base "):
            selections["subrace"] = None  # Base means no subrace modifiers

        # ---------------------------
        # 5) Class selection (menu)
        # ---------------------------
        selections["class"] = select_class(classes)
        if selections["class"] not in classes:
            logger.error(f"Selected class '{selections['class']}' not in classes dictionary.")
            print(f"{Fore.RED}Error: Selected class not found. Please check your data files.{Style.RESET_ALL}")
            return None

        # ---------------------------
        # 6) Cleric domain (optional)
        # ---------------------------
        selections["domain"] = _select_cleric_domain_if_needed(selections["class"])

        # ---------------------------
        # 7) Roll/allocate stats
        # ---------------------------
        # We delegate manual/random logic to your existing stat_roller.roll_stats,
        # which should compute both ordered list and a labeled dict of final stats.
        selections["stats"], selections["stat_dict"] = roll_stats(
            race=selected_race,
            subrace=selections["subrace"],
            classes=classes,
            class_name=selections["class"],
            subclass_name=selections["domain"],
            character_level=1
        )

        # ---------------------------
        # 8) Pick starting spells
        # ---------------------------
        selections["spells"] = select_spells(
            selections["class"],
            character_level=1,
            stat_dict=selections["stat_dict"],
            domain=selections["domain"]
        )

        # ---------------------------
        # 9) Final review/confirm
        # ---------------------------
        confirmed = review_selections(selections, races, classes)
        if not confirmed:
            print(f"{Fore.YELLOW}Character creation cancelled.{Style.RESET_ALL}")
            logger.info("Character creation cancelled by user")
            return None

        # ---------------------------
        # 10) Create Character model
        # ---------------------------
        character = Character(
            name=name,
            race=selections["race"],
            subrace_name=selections["subrace"],
            class_name=selections["class"],
            stats=selections["stat_dict"],
            known_spells=selections["spells"],
            domain=selections["domain"]
        )
        logger.info(
            "Character created: %s, %s, %s, %s",
            name, selections['race'], selections['subrace'], selections['class']
        )
        return character

    except SystemExit as e:
        # Graceful "quit" path from within selection menus
        print(f"{Fore.YELLOW}{str(e)}{Style.RESET_ALL}")
        logger.info(f"Character creation cancelled: {str(e)}")
        return None
