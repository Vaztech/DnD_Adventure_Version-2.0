import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

def console_print(message: str, color: str = "white"):
    """Print a message to the console with the specified color."""
    color_map = {
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "green": Fore.GREEN,
        "blue": Fore.BLUE
    }
    color_code = color_map.get(color.lower(), Fore.WHITE)
    print(f"{color_code}{message}{Style.RESET_ALL}")
    logger.debug(f"Console print: {message}")

def console_input(prompt: str, color: str = "white") -> str:
    """Prompt the user for input with the specified color."""
    color_map = {
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "green": Fore.GREEN,
        "blue": Fore.BLUE
    }
    color_code = color_map.get(color.lower(), Fore.WHITE)
    try:
        user_input = input(f"{color_code}{prompt}{Style.RESET_ALL}")
        logger.debug(f"Console input prompt: {prompt}, received: {user_input}")
        return user_input
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt during console input")
        return ""