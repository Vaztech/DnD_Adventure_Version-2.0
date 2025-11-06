import logging
import keyboard
import time

logger = logging.getLogger(__name__)

def handle_input(game):
    logger.debug("Checking input for game mode: %s", game.mode)
    
    if game.mode == "movement":
        key_map = {
            'w': 'w',
            's': 's',
            'a': 'a',
            'd': 'd',
            'enter': 'enter',
            'escape': 'help',
            'f12': 'debug'
        }
        try:
            for key in key_map:
                if keyboard.is_pressed(key):
                    logger.debug(f"Key pressed: {key}")
                    command = key_map[key]
                    logger.debug(f"Returning command: {command}")
                    time.sleep(0.1)  # Debounce to prevent multiple detections
                    return command
            logger.debug("No keypress detected")
            return None
        except Exception as e:
            logger.error(f"Input error: {e}")
            return None
    else:  # command mode
        try:
            command = input("Enter command: ").strip().lower()
            logger.debug(f"Command input: {command}")
            return command
        except Exception as e:
            logger.error(f"Command input error: {e}")
            return None