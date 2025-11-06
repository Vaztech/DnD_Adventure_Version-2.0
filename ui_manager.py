import os
from colorama import Fore, Style
from .lore_manager import LoreManager
from .utils import console_print, console_input

class UIManager:
    def __init__(self, game):
        self.game = game
        self.themes_dir = os.path.join(os.path.dirname(__file__), 'data', 'themes')
        self.lore_manager = LoreManager(self.themes_dir)

    def display_lore_screen(self, theme: str):
        """Display the lore intro on a standalone screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.lore_manager.print_lore(theme)
        console_input("Press Enter to continue...", color="yellow")
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_current_map(self):
        """Display the current game map."""
        room = self.game.game_world.get_room(self.game.current_room)
        if not room:
            console_print("Error: No room found!", color="red")
            return
        console_print(f"You are in {room.name}.", color="cyan")
        console_print(room.description, color="cyan")
        if room.npcs:
            console_print(f"NPCs present: {', '.join(npc.name for npc in room.npcs)}", color="cyan")
        # Placeholder for map rendering (update as per your ui.py)
        console_print(f"Map: {self.game.current_map}", color="cyan")