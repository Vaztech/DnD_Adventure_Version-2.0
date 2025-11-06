import os
from typing import Dict, List, Optional
import logging
from colorama import Fore, Style
from dnd_adventure.race_selector import select_race
from dnd_adventure.class_selector import select_class
from dnd_adventure.stat_roller import roll_stats
from dnd_adventure.spell_selector import select_spells
from dnd_adventure.selection_reviewer import review_selections
from dnd_adventure.character import Character
from dnd_adventure.race_models import Race  # Added import

logger = logging.getLogger(__name__)

def create_player(name: str, game: object) -> 'Character':
    logger.debug("Creating new player")
    # Convert races to Race objects if they're dictionaries
    races = [
        Race(**r) if isinstance(r, dict) else r
        for r in game.races
    ]
    classes = game.classes
    selections = {
        "race": None,
        "subrace": None,
        "class": None,
        "stats": None,
        "stat_dict": None,
        "spells": None,
        "domain": None
    }

    try:
        selections["race"] = select_race(races)
        selected_race = next((r for r in races if r.name == selections["race"]), None)
        if selected_race and selected_race.subraces:
            subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"\n{Fore.CYAN}=== Select Your Subrace ==={Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                for i, subrace in enumerate(subrace_names, 1):
                    if subrace.startswith("Base "):
                        desc = f"Standard {selections['race']} with no subrace-specific traits."
                        modifiers = "No additional modifiers"
                    else:
                        subrace_data = selected_race.subraces.get(subrace, {})
                        desc = subrace_data.get("description", "No description available")
                        desc = desc[:100] + "..." if len(desc) > 100 else desc
                        modifiers = subrace_data.get("stat_bonuses", {})
                        modifiers_str = ", ".join(f"{k}: {v:+d}" for k, v in modifiers.items()) or "No modifiers"
                    print(f"{Fore.YELLOW}{i}. {subrace}{Style.RESET_ALL}")
                    print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                    print(f"     {Fore.LIGHTYELLOW_EX}Modifiers: {modifiers_str}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                try:
                    choice = input(f"\n{Fore.CYAN}Enter number (or 'q' to quit): {Style.RESET_ALL}").strip().lower()
                    if choice == 'q':
                        logger.info("Game exited during subrace selection")
                        raise SystemExit("Subrace selection cancelled")
                    choice = int(choice) - 1
                    if 0 <= choice < len(subrace_names):
                        selections["subrace"] = subrace_names[choice]
                        logger.debug(f"Selected subrace: {selections['subrace']}")
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select a number between 1 and {len(subrace_names)}.{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number or 'q'.{Style.RESET_ALL}")
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

        selections["class"] = select_class(classes)
        selected_class = classes.get(selections["class"])
        if selections["class"] == "Cleric":
            domains = ["Air", "Death", "Healing", "War"]
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"\n{Fore.CYAN}=== Select a Cleric Domain ==={Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
                for i, domain in enumerate(domains, 1):
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
                    choice = int(choice) - 1
                    if 0 <= choice < len(domains):
                        selections["domain"] = domains[choice]
                        logger.debug(f"Selected domain: {selections['domain']}")
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice. Please select a number between 1 and {len(domains)}.{Style.RESET_ALL}")
                        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number or 'q'.{Style.RESET_ALL}")
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

        selections["stats"], selections["stat_dict"] = roll_stats(
            race=selected_race,
            subrace=selections["subrace"],
            classes=classes,
            class_name=selections["class"],
            subclass_name=selections["domain"],
            character_level=1
        )
        selections["spells"] = select_spells(
            selections["class"],
            character_level=1,
            stat_dict=selections["stat_dict"],
            domain=selections["domain"]
        )

        confirmed = review_selections(selections, races, classes)
        if not confirmed:
            print(f"{Fore.YELLOW}Character creation cancelled.{Style.RESET_ALL}")
            logger.info("Character creation cancelled by user")
            return None

        character = Character(
            name=name,
            race=selections["race"],
            subrace_name=selections["subrace"],
            class_name=selections["class"],
            stats=selections["stat_dict"],
            known_spells=selections["spells"],
            domain=selections["domain"]
        )
        logger.info(f"Character created: {name}, {selections['race']}, {selections['subrace']}, {selections['class']}")
        return character
    except SystemExit as e:
        print(f"{Fore.YELLOW}{str(e)}{Style.RESET_ALL}")
        logger.info(f"Character creation cancelled: {str(e)}")
        return None