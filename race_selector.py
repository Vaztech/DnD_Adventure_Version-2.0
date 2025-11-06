import os
import logging
from typing import List
from colorama import Fore, Style
from dnd_adventure.race_models import Race  # Import Race class for type hint

logger = logging.getLogger(__name__)

def select_race(races: List[Race]) -> str:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Your Race ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, race in enumerate(races, 1):
            desc = race.description[:100] + "..." if len(race.description) > 100 else race.description
            modifiers = getattr(race, 'stat_bonuses', getattr(race, 'ability_modifiers', {}))
            modifiers_str = ", ".join(f"{k}: {v:+d}" for k, v in modifiers.items()) or "No modifiers"
            print(f"{Fore.YELLOW}{i}. {race.name}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}Modifiers: {modifiers_str}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your chosen race (or 'q' to quit):{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'q':
            logger.info("Game exited during race selection")
            raise SystemExit("Race selection cancelled")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(races):
                logger.debug(f"Selected race: {races[choice_index].name}")
                return races[choice_index].name
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(races)}.{Style.RESET_ALL}")
                logger.warning(f"Invalid race choice: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to quit.{Style.RESET_ALL}")
            logger.warning(f"Invalid race input: {choice}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def select_subrace(subrace_names: List[str], race: Race) -> str:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}=== Select Subrace for {race.name} ==={Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        for i, subrace in enumerate(subrace_names, 1):
            if subrace.startswith("Base "):
                desc = f"Standard {race.name} with no subrace-specific traits."
                modifiers = race.subraces[subrace].get("stat_bonuses", race.subraces[subrace].get("ability_modifiers", {}))
                modifiers_str = "No additional modifiers"
            else:
                desc = race.subraces[subrace]["description"]
                desc = desc[:100] + "..." if len(desc) > 100 else desc
                modifiers = race.subraces[subrace].get("stat_bonuses", race.subraces[subrace].get("ability_modifiers", {}))
                modifiers_str = ", ".join(f"{k}: {v:+d}" for k, v in modifiers.items()) or "No modifiers"
            print(f"{Fore.YELLOW}{i}. {subrace}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
            print(f"     {Fore.LIGHTYELLOW_EX}Modifiers: {modifiers_str}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Enter the number of your chosen subrace (or 'q' to quit):{Style.RESET_ALL}")
        choice = input().strip().lower()
        if choice == 'q':
            logger.info("Game exited during subrace selection")
            raise SystemExit("Subrace selection cancelled")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(subrace_names):
                logger.debug(f"Selected subrace: {subrace_names[choice_index]}")
                return subrace_names[choice_index]
            else:
                print(f"{Fore.RED}Invalid choice! Please select a number between 1 and {len(subrace_names)}.{Style.RESET_ALL}")
                logger.warning(f"Invalid subrace choice: {choice}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number or 'q' to quit.{Style.RESET_ALL}")
            logger.warning(f"Invalid subrace input: {choice}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")