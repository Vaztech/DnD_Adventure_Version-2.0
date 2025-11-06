from colorama import Fore, Style
import logging

logger = logging.getLogger(__name__)

def console_print(text, color="white", flush=False):
    color_map = {
        "cyan": Fore.CYAN,
        "yellow": Fore.YELLOW,
        "red": Fore.RED,
        "white": Fore.WHITE
    }
    try:
        print(f"{color_map.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}", flush=flush)
        logger.debug(f"Console print: {text}")
    except Exception as e:
        logger.error(f"Console print error: {e}")

def console_input(prompt, color="white"):
    color_map = {
        "cyan": Fore.CYAN,
        "yellow": Fore.YELLOW,
        "red": Fore.RED,
        "white": Fore.WHITE
    }
    try:
        return input(f"{color_map.get(color, Fore.WHITE)}{prompt}{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Console input error: {e}")
        return ""