import logging
from typing import Optional, Any
from .console_utils import console_print, console_input

logger = logging.getLogger(__name__)

class ClassManager:
    def __init__(self):
        self.preferred_stats = {
            "Barbarian": "Strength",
            "Bard": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Fighter": "Strength",
            "Monk": "Dexterity",
            "Paladin": "Charisma",
            "Ranger": "Dexterity",
            "Rogue": "Dexterity",
            "Sorcerer": "Charisma",
            "Wizard": "Intelligence",
            "Assassin": "Dexterity"
        }

    def select_class(self, game: Any) -> Optional[str]:
        logger.debug("Starting class selection")
        classes = game.classes
        
        while True:
            console_print("=== Select Your Class ===", color="cyan")
            class_list = list(classes.items())
            for i, (class_name, class_data) in enumerate(class_list, 1):
                console_print("----------------------------------------", color="cyan")
                console_print(f"{i}. {class_name}", color="cyan")
                console_print(f"     {class_data.get('description', '')}", color="cyan")
                console_print(f"     Preferred Stat: {self.preferred_stats.get(class_name, 'Unknown')}", color="cyan")
            console_print("----------------------------------------", color="cyan")
            selection = console_input(f"Select class (1-{len(class_list)}): ", color="yellow").strip()
            
            logger.debug(f"Selected class: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(class_list):
                    return class_list[index][0]
            console_print(f"Invalid class selected. Please enter a number (1-{len(class_list)}).", color="red")

    def select_subclass(self, game: Any, character_class: str, level: int) -> Optional[str]:
        logger.debug(f"Selecting subclass for {character_class}")
        class_data = game.classes.get(character_class, {})
        subclasses = class_data.get("subclasses", {})
        if not subclasses:
            logger.debug(f"No subclasses available for {character_class}")
            return None
        
        unlocked_subclasses = []
        for subclass_name, data in subclasses.items():
            prereqs = data.get("prerequisites", {})
            level_req = prereqs.get("level", 1)
            stat_reqs = prereqs.get("stats", {})
            if level >= level_req:
                unlocked_subclasses.append((subclass_name, data))
        
        if not unlocked_subclasses:
            logger.debug(f"No unlocked subclasses for {character_class} at level {level}")
            return None
        
        while True:
            console_print("=== Select Your Subclass (or None) ===", color="cyan")
            for i, (subclass_name, data) in enumerate(unlocked_subclasses, 1):
                console_print("----------------------------------------", color="cyan")
                console_print(f"{i}. {subclass_name}", color="cyan")
                console_print(f"     {data.get('description', '')}", color="cyan")
            console_print("----------------------------------------", color="cyan")
            console_print(f"{len(unlocked_subclasses) + 1}. None", color="cyan")
            selection = console_input(f"Select subclass (1-{len(unlocked_subclasses) + 1}): ", color="yellow").strip()
            
            logger.debug(f"Selected subclass: {selection}")
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(unlocked_subclasses):
                    return unlocked_subclasses[index][0]
                elif index == len(unlocked_subclasses):
                    return None
            console_print(f"Invalid selection. Please enter a number (1-{len(unlocked_subclasses) + 1}).", color="red")