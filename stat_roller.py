import random
import logging
from typing import List, Optional, Dict, Tuple
from colorama import Fore, Style
from dnd_adventure.races import Race

logger = logging.getLogger(__name__)

def roll_stats(race: Race, subrace: Optional[str], classes: Dict, class_name: str, subclass_name: Optional[str] = None, character_level: int = 1) -> Tuple[List[int], Dict[str, int]]:
    stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    stats = []
    print(f"\n{Fore.CYAN}=== Rolling Stats (4d6, drop lowest) ==={Style.RESET_ALL}")
    logger.debug("Rolling stats")
    for i in range(6):
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.remove(min(rolls))
        stat = sum(rolls)
        stats.append(stat)
        print(f"{stat_names[i]}: {stat}")
    print(f"\n{Fore.YELLOW}=== Applying Bonuses ==={Style.RESET_ALL}")
    racial_mods = race.ability_modifiers
    if racial_mods:
        print(f"{Fore.YELLOW}Racial Bonuses ({race.name}):{Style.RESET_ALL}")
        for stat, mod in racial_mods.items():
            print(f"  {stat}: {'+' if mod >= 0 else ''}{mod}")
    else:
        print(f"{Fore.YELLOW}Racial Bonuses ({race.name}): None{Style.RESET_ALL}")
    subrace_mods = {}
    if subrace and subrace != "Base " + race.name and race.subraces and subrace in race.subraces:
        subrace_mods = race.subraces[subrace].get("ability_modifiers", {})
        if subrace_mods:
            print(f"{Fore.YELLOW}Subrace Bonuses ({subrace}):{Style.RESET_ALL}")
            for stat, mod in subrace_mods.items():
                print(f"  {stat}: {'+' if mod >= 0 else ''}{mod}")
        else:
            print(f"{Fore.YELLOW}Subrace Bonuses ({subrace}): None{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Subrace Bonuses: None{Style.RESET_ALL}")
    stat_indices = {name: i for i, name in enumerate(stat_names)}
    modified_stats = stats.copy()
    for stat, mod in racial_mods.items():
        if stat in stat_indices:
            modified_stats[stat_indices[stat]] += mod
    for stat, mod in subrace_mods.items():
        if stat in stat_indices:
            modified_stats[stat_indices[stat]] += mod
    dnd_class = classes.get(class_name)
    if dnd_class:
        print(f"{Fore.YELLOW}Class Bonuses ({class_name}):{Style.RESET_ALL}")
        class_skills = dnd_class.get("class_skills", [])
        if class_skills:
            print(f"  Class Skills: {', '.join(class_skills)}")
        else:
            print(f"  No class skills defined")
        if dnd_class.get("features"):
            print(f"  Features:")
            for feature in dnd_class["features"]:
                print(f"    - {feature['name']}: {feature['description']}")
        if subclass_name and dnd_class.get("subclasses", {}).get(subclass_name):
            print(f"{Fore.YELLOW}Subclass Bonuses ({subclass_name}):{Style.RESET_ALL}")
            subclass = dnd_class["subclasses"][subclass_name]
            subclass_skills = subclass.get("class_skills", [])
            if subclass_skills:
                print(f"  Subclass Skills: {', '.join(subclass_skills)}")
            else:
                print(f"  No subclass skills defined")
            if subclass.get("features"):
                print(f"  Subclass Features:")
                for feature in subclass["features"]:
                    print(f"    - {feature['name']}: {feature['description']}")
        if dnd_class.get("subclasses"):
            print(f"\n{Fore.YELLOW}Available Subclasses at Level {character_level}:{Style.RESET_ALL}")
            for subclass_name, subclass in dnd_class["subclasses"].items():
                prereqs = subclass.get("prerequisites", {})
                level_req = prereqs.get("level", 1)
                stat_reqs = prereqs.get("stats", {})
                can_access = character_level >= level_req
                for stat, req in stat_reqs.items():
                    stat_index = stat_indices.get(stat)
                    if stat_index is None or modified_stats[stat_index] < req:
                        can_access = False
                status = Fore.GREEN + "Unlocked" if can_access else Fore.RED + "Locked"
                print(f"  {subclass_name} ({status}{Style.RESET_ALL}): {subclass['description']}")
                if level_req > 1 or stat_reqs:
                    print(f"    Requirements:")
                    if level_req > 1:
                        print(f"      - Level: {level_req}")
                    for stat, req in stat_reqs.items():
                        print(f"      - {stat}: {req}")
    else:
        print(f"{Fore.YELLOW}Class Bonuses: None{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}=== Final Stats ==={Style.RESET_ALL}")
    for i, stat in enumerate(modified_stats):
        print(f"{stat_names[i]}: {stat}")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    stat_dict = {name: modified_stats[i] for i, name in enumerate(stat_names)}
    logger.debug(f"Stats rolled: {modified_stats}, Dict: {stat_dict}")
    return modified_stats, stat_dict