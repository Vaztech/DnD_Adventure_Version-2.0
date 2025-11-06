# dnd_adventure/main.py
import logging
import time
import os
import sys
from colorama import init, Fore, Style

# ✅ Cross-platform single-key input (no direct 'import msvcrt')
from .msvcrt_compat import kbhit, getch

# ✅ Relative imports (because main.py is inside the dnd_adventure package)
from .game import Game
from .input_handler import handle_input
from .ui import UIManager
from .logging_config import setup_logging

# PlayerManager is in an external package folder per your project layout
from .player_manager.player_manager import PlayerManager

setup_logging()
logger = logging.getLogger(__name__)

def display_start_menu():
    print(f"{Fore.CYAN}=== D&D Adventure ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}1. New Game{Style.RESET_ALL}")
    print(f"{Fore.CYAN}2. Continue Game{Style.RESET_ALL}")
    print(f"{Fore.CYAN}3. Select Character{Style.RESET_ALL}")
    print(f"{Fore.CYAN}4. Delete Character{Style.RESET_ALL}")
    print(f"{Fore.CYAN}5. Exit{Style.RESET_ALL}")
    choice = input(f"{Fore.YELLOW}Select an option (1-5): {Style.RESET_ALL}").strip()
    return choice

def main():
    try:
        init()  # colorama init
        logger.info("Starting D&D Adventure")

        player_manager = PlayerManager()

        # Start menu loop
        while True:
            choice = display_start_menu()

            if choice == "1":  # New Game
                player_name = input(f"{Fore.YELLOW}Enter your character name: {Style.RESET_ALL}").strip()
                if not player_name:
                    print(f"{Fore.RED}Name cannot be empty!{Style.RESET_ALL}")
                    continue
                game = Game(player_name, player_manager, None)
                if not getattr(game, "running", True):
                    print(f"{Fore.RED}Failed to start new game!{Style.RESET_ALL}")
                    continue
                break

            elif choice == "2":  # Continue Game
                save_files = Game.list_save_files()
                if not save_files:
                    print(f"{Fore.RED}No save files found!{Style.RESET_ALL}")
                    continue
                print(f"{Fore.YELLOW}Available save files: {', '.join(save_files)}{Style.RESET_ALL}")
                save_file = input(f"{Fore.YELLOW}Enter save file name: {Style.RESET_ALL}").strip()
                if save_file not in save_files:
                    print(f"{Fore.RED}Save file not found!{Style.RESET_ALL}")
                    continue
                game = Game(None, player_manager, save_file)
                if not getattr(game, "running", True):
                    print(f"{Fore.RED}Failed to load game!{Style.RESET_ALL}")
                    continue
                break

            elif choice == "3":  # Select Character
                save_files = Game.list_save_files()
                if not save_files:
                    print(f"{Fore.RED}No characters found!{Style.RESET_ALL}")
                    continue
                print(f"{Fore.YELLOW}Available characters: {', '.join(save_files)}{Style.RESET_ALL}")
                save_file = input(f"{Fore.YELLOW}Enter character save file name: {Style.RESET_ALL}").strip()
                if save_file not in save_files:
                    print(f"{Fore.RED}Character not found!{Style.RESET_ALL}")
                    continue
                game = Game(None, player_manager, save_file)
                if not getattr(game, "running", True):
                    print(f"{Fore.RED}Failed to load character!{Style.RESET_ALL}")
                    continue
                break

            elif choice == "4":  # Delete Character
                save_files = Game.list_save_files()
                if not save_files:
                    print(f"{Fore.RED}No characters to delete!{Style.RESET_ALL}")
                    continue
                print(f"{Fore.YELLOW}Available characters: {', '.join(save_files)}{Style.RESET_ALL}")
                save_file = input(f"{Fore.YELLOW}Enter character save file name to delete: {Style.RESET_ALL}").strip()
                if save_file not in save_files:
                    print(f"{Fore.RED}Character not found!{Style.RESET_ALL}")
                    continue
                try:
                    os.remove(os.path.join("dnd_adventure", "data", "saves", save_file))
                    print(f"{Fore.CYAN}Character deleted successfully!{Style.RESET_ALL}")
                    logger.info(f"Deleted save file: {save_file}")
                except Exception as e:
                    print(f"{Fore.RED}Failed to delete character: {e}{Style.RESET_ALL}")
                    logger.error(f"Failed to delete save file {save_file}: {e}")

            elif choice == "5":  # Exit
                print(f"{Fore.CYAN}Exiting D&D Adventure. Goodbye!{Style.RESET_ALL}")
                return

            else:
                print(f"{Fore.RED}Invalid option! Please select 1-5.{Style.RESET_ALL}")

        # --- Main game loop ---
        last_enter_time = 0.0
        enter_press_count = 0
        DOUBLE_PRESS_TIMEOUT = 0.5  # seconds
        last_displayed = None  # Track last displayed state

        while getattr(game, "running", True):
            logger.debug(f"Game mode: {getattr(game, 'mode', 'movement')}")
            current_state = (getattr(game, "player_pos", None),
                             getattr(game, "mode", None),
                             getattr(game, "message", None))

            # Redraw only if state changed
            if current_state != last_displayed:
                if getattr(game, "mode", "movement") == "movement" or (
                    getattr(game, "mode", "movement") == "command" and not getattr(game, "message", "")
                ):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    # UI manager should know how to draw current map
                    game.ui_manager.display_current_map()
                if getattr(game, "message", ""):
                    print(game.message, flush=True)
                last_displayed = current_state

            if getattr(game, "mode", "movement") == "movement":
                command = handle_input(game)
                logger.debug(f"Received command: {command}")
                if command == "enter":
                    now = time.time()
                    if now - last_enter_time < DOUBLE_PRESS_TIMEOUT:
                        enter_press_count += 1
                    else:
                        enter_press_count = 1
                    last_enter_time = now
                    if enter_press_count == 1:
                        game.mode = "command"
                        print(f"{Fore.YELLOW}Enter command: {Style.RESET_ALL}", end="", flush=True)
                elif command in ["w", "s", "a", "d", "help", "debug"]:
                    game.handle_command(command)

            elif getattr(game, "mode", "movement") == "command":
                cmd = input().strip()
                logger.debug(f"Command mode input: {cmd}")
                if cmd:
                    game.handle_command(cmd)
                    enter_press_count = 0
                    if getattr(game, "message", ""):
                        input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                else:
                    now = time.time()
                    if now - last_enter_time < DOUBLE_PRESS_TIMEOUT and enter_press_count >= 1:
                        logger.debug("Double Enter detected, returning to movement mode")
                        game.mode = "movement"
                        enter_press_count = 0
                        # flush any buffered keys
                        while kbhit():
                            _ = getch()
                    else:
                        enter_press_count = 1
                        last_enter_time = now
                        print(f"{Fore.YELLOW}Enter command: {Style.RESET_ALL}", end="", flush=True)

            time.sleep(0.05)  # Ease CPU

    except Exception as e:
        logger.error(f"Game crashed: {e}", exc_info=True)
        print(f"{Fore.RED}Error: Game crashed - {e}. Check dnd_adventure.log for details.{Style.RESET_ALL}")
        try:
            input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
