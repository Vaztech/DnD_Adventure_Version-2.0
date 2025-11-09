import os
import json
import random
from typing import Dict, List, Any

def _data_path(*parts: str) -> str:
    """Return a normalized path to the data/ directory (cross-platform)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))          # .../worldgen
    project_pkg_dir = os.path.dirname(base_dir)                    # .../dnd_adventure
    data_dir = os.path.join(project_pkg_dir, "data")
    return os.path.normpath(os.path.join(data_dir, *parts))

def _load_json(path: str) -> Any:
    """Safely load JSON with clear errors."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing data file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_races() -> List[Dict[str, Any]]:
    """Load race data from data/races.json."""
    races_path = _data_path("races.json")
    return _load_json(races_path)

def simulate_events(civilizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate historical events for world simulation.

    Each event references a civilization and sometimes a race.
    """
    races = load_races()
    events: List[Dict[str, Any]] = []
    event_types = [
        "War",
        "Alliance",
        "Discovery",
        "Rebellion",
        "Coronation",
        "Catastrophe",
        "Plague",
        "Invention",
        "Migration",
    ]

    year = 0
    for _ in range(random.randint(15, 35)):
        year += random.randint(1, 25)
        civ = random.choice(civilizations) if civilizations else None
        race = random.choice(races) if races else {"name": "Unknown"}
        event_type = random.choice(event_types)

        events.append({
            "year": year,
            "type": event_type,
            "civilization": civ["name"] if civ else "Unknown",
            "race": race["name"],
            "description": generate_event_description(event_type, civ, race),
        })

    return events

def generate_event_description(event_type: str, civ: Dict[str, Any], race: Dict[str, Any]) -> str:
    """Generate flavorful text for each event type."""
    civ_name = civ["name"] if civ else "Unknown Civilization"
    race_name = race["name"] if race else "Unknown Race"

    templates = {
        "War": f"A bloody war erupts between the {race_name} and {civ_name}.",
        "Alliance": f"The {race_name} people form an alliance with {civ_name}.",
        "Discovery": f"Explorers from {civ_name} uncover ancient relics of the {race_name}.",
        "Rebellion": f"A rebellion led by {race_name} dissidents shakes {civ_name}.",
        "Coronation": f"A new ruler of {civ_name}, from the {race_name} lineage, is crowned.",
        "Catastrophe": f"Natural disasters ravage {civ_name}, decimating the {race_name} population.",
        "Plague": f"A terrible plague spreads through {civ_name}, striking both {race_name} and allies.",
        "Invention": f"The {race_name} invent a new tool that revolutionizes life in {civ_name}.",
        "Migration": f"The {race_name} migrate en masse toward the borders of {civ_name}.",
    }
    return templates.get(event_type, f"An undefined event involving {civ_name} and {race_name} occurred.")

# Quick test harness
if __name__ == "__main__":
    civs = [
        {"name": "Dwarf Empire", "race": "Dwarf"},
        {"name": "Elven Dominion", "race": "Elf"},
    ]
    evts = simulate_events(civs)
    print(json.dumps(evts[:5], indent=2))
