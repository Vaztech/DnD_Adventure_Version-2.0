import json
import logging
import os
from typing import Dict
from colorama import Fore, Style
from dnd_adventure.character import Character

logger = logging.getLogger(__name__)

def load_classes() -> Dict:
    # Use absolute path relative to leveling.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    classes_path = os.path.join(base_dir, "data", "classes.json")
    try:
        with open(classes_path, "r", encoding="utf-8") as f:
            classes = json.load(f)
            logger.debug(f"Loaded classes.json from {classes_path}")
            return classes
    except FileNotFoundError:
        logger.error(f"classes.json not found at {classes_path}")
        raise FileNotFoundError(f"Could not find {classes_path}. Ensure the file exists in the data directory.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in classes.json: {e}")
        raise ValueError(f"Invalid JSON in classes.json: {e}")

def level_up(character: Character, classes: Dict) -> bool:
    current_level = character.level
    next_level = current_level + 1
    xp_required = 300 * (3 ** (next_level - 2)) if next_level >= 2 else 0
    if character.xp >= xp_required and next_level <= 20:
        character.level = next_level
        hit_die = classes[character.class_name]["hit_die"]
        con_mod = (character.stat_dict["Constitution"] - 10) // 2
        new_hp = (hit_die // 2 + 1) + con_mod
        character.max_hit_points += max(1, new_hp)
        character.hit_points = character.max_hit_points
        character.max_mp += 3
        character.mp = character.max_mp
        print(f"\n{Fore.GREEN}Congratulations! {character.name} has reached level {character.level}!{Style.RESET_ALL}")
        print(f"HP increased to {character.max_hit_points}, MP increased to {character.max_mp}")
        logger.info(f"Player {character.name} leveled up to {character.level}")
        
        dnd_class = classes.get(character.class_name, {})
        unlocked_subclasses = []
        for subclass_name, subclass in dnd_class.get("subclasses", {}).items():
            if character.check_subclass_eligibility(classes, subclass_name) and character.subclass_name != subclass_name:
                unlocked_subclasses.append((subclass_name, subclass))
        
        if unlocked_subclasses:
            print(f"\n{Fore.YELLOW}New subclasses unlocked!{Style.RESET_ALL}")
            for i, (subclass_name, subclass) in enumerate(unlocked_subclasses, 1):
                print(f"{i}. {subclass_name}: {subclass['description']}")
            print("0. Keep current class/subclass")
            try:
                choice = int(input("Select a subclass (0 to skip): "))
                if 0 < choice <= len(unlocked_subclasses):
                    selected_subclass = unlocked_subclasses[choice - 1][0]
                    character.subclass_name = selected_subclass
                    subclass_data = dnd_class["subclasses"][selected_subclass]
                    character.class_skills.extend(subclass_data.get("class_skills", []))
                    character.features.extend(subclass_data.get("features", []))
                    if subclass_data.get("spellcasting"):
                        # Placeholder: Add spell selection
                        pass
                    print(f"Subclass set to {selected_subclass}")
                    logger.info(f"Player {character.name} selected subclass {selected_subclass}")
            except ValueError:
                print("Invalid input, keeping current class/subclass")
                logger.warning("Invalid subclass selection input")
        return True
    return False