import os
import logging
from typing import Dict
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def select_class(classes: Dict) -> str:
    logger.debug("Starting class selection")
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    class_list = []
    for class_name, class_data in classes.items():
        # Skip subclasses with prerequisites (e.g., Assassin, Archmage)
        if 'prerequisites' in class_data and class_data['prerequisites'].get('level', 1) > 1:
            continue
        class_list.append((class_name, class_data))
    for i, (class_name, class_data) in enumerate(class_list, 1):
        desc = class_data.get("description", "No description available")
        desc = desc[:100] + "..." if len(desc) > 100 else desc
        print(f"{Fore.YELLOW}{i}. {class_name}{Style.RESET_ALL}")
        print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter number (or 'q' to quit): {Style.RESET_ALL}").strip().lower()
            if choice == 'q':
                logger.info("Game exited during class selection")
                raise SystemExit("Class selection cancelled")
            choice = int(choice) - 1
            if 0 <= choice < len(class_list):
                selected_class = class_list[choice][0]
                logger.debug(f"Selected class: {selected_class}")
                return selected_class
            print(f"{Fore.RED}Invalid choice. Please select a number between 1 and {len(class_list)}.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            for i, (class_name, class_data) in enumerate(class_list, 1):
                desc = class_data.get("description", "No description available")
                desc = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"{Fore.YELLOW}{i}. {class_name}{Style.RESET_ALL}")
                print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number or 'q'.{Style.RESET_ALL}")
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{Fore.CYAN}=== Select Your Class ==={Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
            for i, (class_name, class_data) in enumerate(class_list, 1):
                desc = class_data.get("description", "No description available")
                desc = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"{Fore.YELLOW}{i}. {class_name}{Style.RESET_ALL}")
                print(f"     {Fore.LIGHTYELLOW_EX}{desc}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")