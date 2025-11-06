import os
import logging
from typing import Dict, List, Optional
from colorama import Fore, Style
from dnd_adventure.data_loaders.spell_loader import SpellLoader
from dnd_adventure.spells import CORE_SPELLS, Spell

logger = logging.getLogger(__name__)

def select_spells(class_name: str, character_level: int, stat_dict: Dict[str, int], domain: Optional[str] = None) -> Dict[int, List[str]]:
    spellcasting_classes = ["Wizard", "Sorcerer", "Cleric", "Druid", "Bard", "Paladin", "Ranger"]
    if class_name not in spellcasting_classes:
        logger.debug(f"No spells available for non-spellcasting class: {class_name}")
        return {0: [], 1: []}

    loader = SpellLoader()
    spells = loader.load_spells_from_json()
    class_key = "Sorcerer/Wizard" if class_name in ["Wizard", "Sorcerer"] else class_name
    available_spells = spells.get(class_key, {0: [], 1: []})

    if not any(available_spells.get(i) for i in range(10)):
        logger.warning(f"No spells loaded for {class_name}, using CORE_SPELLS")
        available_spells = {
            i: [s for s in CORE_SPELLS.values() if s.level == i and class_name in s.classes]
            for i in range(10)
        }

    max_spells = {
        "Wizard": {0: 4, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2},
        "Sorcerer": {0: 4, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2},
        "Cleric": {0: 4, 1: 2 + (1 if domain else 0), 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2},
        "Druid": {0: 4, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2},
        "Bard": {0: 4, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2},
        "Paladin": {1: 1, 2: 1, 3: 1, 4: 1},
        "Ranger": {1: 1, 2: 1, 3: 1, 4: 1}
    }.get(class_name, {i: 0 for i in range(10)})

    selected_spells = {i: [] for i in range(10)}
    preferred_stat = {
        "Wizard": "Intelligence",
        "Sorcerer": "Charisma",
        "Cleric": "Wisdom",
        "Druid": "Wisdom",
        "Bard": "Charisma",
        "Paladin": "Wisdom",
        "Ranger": "Wisdom"
    }.get(class_name, "Intelligence")

    for level in range(10):
        if level not in available_spells or not available_spells[level]:
            logger.debug(f"No level {level} spells available for {class_name}")
            continue
        if max_spells.get(level, 0) == 0:
            continue

        spell_options = [
            spell for spell in available_spells[level]
            if spell.name not in selected_spells[level]
            and spell.min_level <= character_level
            and (not spell.primary_stat or stat_dict.get(spell.primary_stat, 0) >= spell.stat_requirement.get(spell.primary_stat, 0))
            and (class_name != "Cleric" or not domain or spell.domain in [None, domain])
        ]
            
        while len(selected_spells[level]) < max_spells.get(level, 0):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}=== Select Level {level} Spells for {class_name} ({len(selected_spells[level])}/{max_spells[level]}) ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            
            if not spell_options:
                logger.debug(f"No more level {level} spells available for {class_name}")
                break
            for i, spell in enumerate(spell_options, 1):
                mp_cost = spell.mp_cost
                stat_req = f"{spell.primary_stat}: {spell.stat_requirement.get(spell.primary_stat, 'N/A')}" if spell.primary_stat else "None"
                domain_info = f" ({spell.domain} Domain)" if spell.domain else ""
                print(f"{Fore.YELLOW}{i}. {spell.name}{domain_info} ({mp_cost} MP){Style.RESET_ALL}")
                print(f"  {Fore.LIGHTYELLOW_EX}Stat Requirement: {stat_req}{Style.RESET_ALL}")
                desc = spell.description[:100] + "..." if len(spell.description) > 100 else spell.description
                print(f"  {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            
            print(f"\n{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Enter the number of the spell to select (or 0 to skip):{Style.RESET_ALL}")
            choice = input().strip()
            
            try:
                choice_idx = int(choice)
                if choice_idx == 0:
                    break
                if not 1 <= choice_idx <= len(spell_options):
                    print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(spell_options)} or 0 to skip.{Style.RESET_ALL}")
                    logger.warning(f"Invalid spell selection choice: {choice}")
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    continue
                selected_spell = spell_options[choice_idx - 1].name
                selected_spells[level].append(selected_spell)
                spell_options.pop(choice_idx - 1)
                logger.debug(f"Selected spell {selected_spell} (Level {level}) for {class_name}")
            except ValueError:
                print(f"{Fore.RED}Invalid input! Please enter a number.{Style.RESET_ALL}")
                logger.warning(f"Invalid spell selection input: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                continue

    logger.debug(f"Final spell selections for {class_name}: {selected_spells}")
    return selected_spells