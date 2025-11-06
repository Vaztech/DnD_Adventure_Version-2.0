import json
import logging
import os
from typing import Optional, Dict, List, Any
from .console_utils import console_print, console_input

logger = logging.getLogger(__name__)

class RaceManager:
    def __init__(self):
        self.races: List[Dict[str, Any]] = []
        races_path = os.path.join(os.path.dirname(__file__), "..", "dnd_adventure", "data", "races.json")
        logger.debug(f"Loading races from {races_path}...")
        try:
            with open(races_path, "r") as f:
                self.races = json.load(f)
            logger.debug(f"Loaded races: {self.races}")
        except FileNotFoundError:
            logger.error(f"Races file not found at {races_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding races.json: {e}")

    def select_race(self) -> Optional[str]:
        while True:
            console_print("=== Select Your Race ===", color="cyan")
            for i, race in enumerate(self.races, 1):
                console_print("----------------------------------------", color="cyan")
                console_print(f"{i}. {race['name']}", color="cyan")
                console_print(f"     {race['description']}", color="cyan")
                modifiers = race.get("ability_modifiers", {})
                modifier_str = self.format_modifiers(modifiers)
                console_print(f"     Stat Modifiers: {modifier_str or 'None'}", color="cyan")
            console_print("----------------------------------------", color="cyan")
            selection = console_input(f"Select race (1-{len(self.races)}): ", color="yellow").strip()
            
            logger.debug(f"Selected race: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(self.races):
                    return self.races[index]["name"]
            console_print(f"Invalid race selected. Please enter a number (1-{len(self.races)}).", color="red")

    def select_subrace(self, race: str) -> Optional[str]:
        race_dict = next((r for r in self.races if r["name"].lower() == race.lower()), None)
        subraces = race_dict.get("subraces", {}) if race_dict else {}
        if not subraces:
            return None
        
        while True:
            console_print("=== Select Your Subrace ===", color="cyan")
            subrace_list = list(subraces.items())
            for i, (subrace_name, subrace_data) in enumerate(subrace_list, 1):
                console_print("----------------------------------------", color="cyan")
                console_print(f"{i}. {subrace_name}", color="cyan")
                console_print(f"     {subrace_data.get('description', '')}", color="cyan")
                modifiers = subrace_data.get("ability_modifiers", {})
                modifier_str = self.format_modifiers(modifiers)
                console_print(f"     Stat Modifiers: {modifier_str or 'None'}", color="cyan")
            console_print("----------------------------------------", color="cyan")
            selection = console_input(f"Select subrace (1-{len(subrace_list)}): ", color="yellow").strip()
            
            logger.debug(f"Selected subrace: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(subrace_list):
                    return subrace_list[index][0]
            console_print(f"Invalid subrace selected. Please enter a number (1-{len(subrace_list)}).", color="red")

    def get_race_data(self, race: str) -> Dict:
        return next((r for r in self.races if r["name"].lower() == race.lower()), {})

    def format_modifiers(self, modifiers: Dict[str, int]) -> str:
        return ", ".join(f"{k}: {'+' if v > 0 else ''}{v}" for k, v in modifiers.items()) if modifiers else ""