import os
import logging
from typing import Dict, List
from colorama import Fore, Style
from dnd_adventure.race_selector import select_race, select_subrace
from dnd_adventure.class_selector import select_class
from dnd_adventure.stat_roller import roll_stats
from dnd_adventure.spell_selector import select_spells

logger = logging.getLogger(__name__)

def review_selections(selections: Dict, races: List, classes: Dict[str, dict]) -> Dict:
    selections = selections or {
        "race": None,
        "subrace": None,
        "class": None,
        "stats": [],
        "stat_dict": {},
        "spells": {0: [], 1: []}
    }
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    options = ["Change race", "Change class", "Reroll stats", "Change spells", "Confirm selections"]
    character_level = 1  # Default for new characters
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Review Your Selections ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        race_display = selections["race"] if not selections["subrace"] or selections["subrace"] == "Base " + selections["race"] else f"{selections['race']} ({selections['subrace']})"
        race_obj = next((r for r in races if r.name == selections["race"]), None)
        race_desc = race_obj.description if race_obj else "Not selected"
        race_desc = race_desc[:100] + "..." if len(race_desc) > 100 else race_desc
        print(f"{Fore.YELLOW}Race: {race_display or 'Not selected'}{Style.RESET_ALL}")
        print(f"  {Fore.LIGHTYELLOW_EX}{race_desc}{Style.RESET_ALL}")
        if race_obj and selections["subrace"] and selections["subrace"] != "Base " + selections["race"]:
            subrace_desc = race_obj.subraces[selections["subrace"]]["description"]
            subrace_desc = subrace_desc[:100] + "..." if len(subrace_desc) > 100 else subrace_desc
            print(f"  {Fore.LIGHTYELLOW_EX}Subrace: {subrace_desc}{Style.RESET_ALL}")
        class_obj = classes.get(selections["class"], None)
        class_desc = class_obj["description"] if class_obj else "Not selected"
        class_desc = class_desc[:100] + "..." if len(class_desc) > 100 else class_desc
        print(f"\n{Fore.YELLOW}Class: {selections['class'] or 'Not selected'}{Style.RESET_ALL}")
        print(f"  {Fore.LIGHTYELLOW_EX}{class_desc}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Stats:{Style.RESET_ALL}")
        for i, stat in enumerate(selections["stats"]):
            print(f"  {stat_names[i]}: {stat}")
        spells_display = "None"
        if selections["spells"] and any(selections["spells"].values()):
            spells_display = ", ".join([f"Level {k}: {', '.join([s.name if hasattr(s, 'name') else str(s) for s in v])}" for k, v in selections["spells"].items() if v])
        print(f"\n{Fore.YELLOW}Spells: {spells_display}{Style.RESET_ALL}")
        print(f"\n{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
        for i, option in enumerate(options, 1):
            print(f"{Fore.YELLOW}{i}. {option}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your choice:{Style.RESET_ALL}")
        choice = input().strip()
        try:
            selected_index = int(choice) - 1
            if not 0 <= selected_index < len(options):
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(options)}.{Style.RESET_ALL}")
                logger.warning(f"Invalid selection review choice: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                continue
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number.{Style.RESET_ALL}")
            logger.warning(f"Invalid selection review input: {choice}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            continue
        if selected_index == 0:
            selections["race"] = select_race(races)
            selected_race = next((r for r in races if r.name == selections["race"]), None)
            if selected_race and selected_race.subraces:
                subrace_names = list(selected_race.subraces.keys()) + ["Base " + selections["race"]]
                selections["subrace"] = select_subrace(subrace_names, selected_race)
            else:
                selections["subrace"] = None
        elif selected_index == 1:
            selections["class"] = select_class(classes)
        elif selected_index == 2:
            selected_race = next((r for r in races if r.name == selections["race"]), None)
            if selected_race:
                selections["stats"], selections["stat_dict"] = roll_stats(selected_race, selections["subrace"], classes, selections["class"], subclass_name=None, character_level=character_level)
        elif selected_index == 3:
            spellcasting_classes = ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Psion"]
            if selections["class"] in spellcasting_classes:
                selections["spells"] = select_spells(selections["class"], character_level, selections["stat_dict"])
                logger.debug(f"Spells reselected for {selections['class']}: {selections['spells']}")
            else:
                selections["spells"] = {0: [], 1: []}
                logger.debug(f"No spells for non-spellcasting class: {selections['class']}")
        elif selected_index == 4:
            logger.debug(f"Selections confirmed: {selections}")
            return selections