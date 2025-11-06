import time
import logging
from colorama import Fore, Style
from dnd_adventure.ui import display_current_map, display_status

logger = logging.getLogger(__name__)

# Import globals from logging_config.py
from dnd_adventure.logging_config import DEBUG_MODE, CONSOLE_HANDLER

# Cache keyboard module and track failures
keyboard_module = None
failed_attempts = 0

def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    CONSOLE_HANDLER.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    status = "enabled" if DEBUG_MODE else "disabled"
    logger.debug(f"Debug console output {status}")
    print(f"{Fore.CYAN}Debug console output {status}{Style.RESET_ALL}")

def handle_keyboard_input(game, current_time: float, last_key_time: float) -> tuple[bool, float, float] | None:
    global keyboard_module, failed_attempts
    if keyboard_module is None:
        try:
            import keyboard
            keyboard_module = keyboard
            logger.debug("Keyboard library initialized successfully")
            failed_attempts = 0
        except ImportError as e:
            logger.warning(f"Failed to import keyboard library: {e}")
            failed_attempts += 1
            return None

    try:
        if current_time - last_key_time < 0.3:
            time.sleep(0.1)
            return game.running, current_time, last_key_time
        if keyboard_module.is_pressed("up") or keyboard_module.is_pressed("w"):
            game.movement_handler.handle_movement("w")
            display_current_map(game)
            display_status(game)
            logger.debug("Keyboard key pressed: up/w")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("down") or keyboard_module.is_pressed("s"):
            game.movement_handler.handle_movement("s")
            display_current_map(game)
            display_status(game)
            logger.debug("Keyboard key pressed: down/s")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("left") or keyboard_module.is_pressed("a"):
            game.movement_handler.handle_movement("a")
            display_current_map(game)
            display_status(game)
            logger.debug("Keyboard key pressed: left/a")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("right") or keyboard_module.is_pressed("d"):
            game.movement_handler.handle_movement("d")
            display_current_map(game)
            display_status(game)
            logger.debug("Keyboard key pressed: right/d")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("enter"):
            if current_time - game.last_enter_time > 0.3:
                game.last_enter_time = current_time
                game.mode = "command"
                display_current_map(game)
                display_status(game)
            logger.debug("Switched to command mode via keyboard")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("esc"):
            display_current_map(game)
            print(f"{Fore.YELLOW}Available commands: {', '.join(game.commands)}{Style.RESET_ALL}")
            display_status(game)
            logger.debug("Displayed help commands via keyboard")
            return game.running, current_time, current_time
        elif keyboard_module.is_pressed("f12"):
            toggle_debug_mode()
            display_current_map(game)
            display_status(game)
            logger.debug("Toggled debug mode via F12")
            return game.running, current_time, current_time
        return None
    except Exception as e:
        logger.error(f"Keyboard library runtime error: {e}")
        print(f"{Fore.YELLOW}Warning: Keyboard library failed.{Style.RESET_ALL}")
        failed_attempts += 1
        return None