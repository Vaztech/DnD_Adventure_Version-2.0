import json
import logging
import os
from typing import List, Optional, Dict
from dnd_adventure.race_models import Race

logger = logging.getLogger(__name__)

def load_races(file_path: str = os.path.join(os.path.dirname(__file__), "data", "races.json")) -> List[Race]:
    try:
        logger.debug(f"Attempting to load races from {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            race_data = json.load(file)
        races = []
        for data in race_data:
            subraces = {
                subrace_name: {
                    "description": subrace_data["description"],
                    "ability_modifiers": subrace_data.get("ability_modifiers", {}),
                    "racial_traits": subrace_data.get("racial_traits", [])
                }
                for subrace_name, subrace_data in data.get("subraces", {}).items()
            }
            race = Race(
                name=data["name"],
                description=data["description"],
                ability_modifiers=data.get("ability_modifiers", {}),
                racial_traits=data.get("racial_traits", []),
                subraces=subraces,
                size=data.get("size", "Medium"),
                speed=data.get("speed", 30),
                favored_class=data.get("favored_class", "Any"),
                languages=data.get("languages", ["Common"])
            )
            races.append(race)
            logger.debug(f"Loaded race: {data['name']} with {len(subraces)} subraces")
        logger.info(f"Loaded {len(races)} races from {file_path}")
        if not races:
            logger.warning("No races loaded from races.json")
        return races
    except FileNotFoundError:
        logger.error(f"Races file not found at {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading races from {file_path}: {e}")
        raise

def get_race_by_name(name: str) -> Optional[Race]:
    races = load_races()
    for race in races:
        if race.name == name:
            return race
    return None

def get_races() -> List[Race]:
    return load_races()

def get_default_race() -> Race:
    races = load_races()
    for race in races:
        if race.name == "Human":
            return race
    return races[0] if races else None