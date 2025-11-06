import os
import json
import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class LoreManager:
    def __init__(self, themes_dir):
        self.themes_dir = themes_dir
        self.lore = {}

    def print_lore(self, theme: str):
        """Load and print lore for the specified theme."""
        theme_file = os.path.join(self.themes_dir, f"{theme}.json")
        try:
            with open(theme_file, 'r') as f:
                self.lore = json.load(f)
            logger.debug(f"Loaded lore for theme {theme}: {self.lore}")
        except FileNotFoundError:
            logger.error(f"Theme file not found: {theme_file}")
            self.lore = {"intro": "No lore available."}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding {theme_file}: {e}")
            self.lore = {"intro": "Invalid lore format."}
        
        intro = self.lore.get("intro", "No lore available.")
        print(f"{Fore.CYAN}{intro}{Style.RESET_ALL}\n")