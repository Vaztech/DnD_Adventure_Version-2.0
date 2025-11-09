# dnd_adventure/worldgen/npc_simulator.py
import os
import json
import random
from typing import Dict, List, Any

def _data_path(*parts: str) -> str:
    """
    Build a normalized cross-platform path to the data/ folder.
    Works for Windows, macOS, and Linux.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))          # .../dnd_adventure/worldgen
    project_pkg_dir = os.path.dirname(base_dir)                    # .../dnd_adventure
    data_dir = os.path.join(project_pkg_dir, "data")               # .../dnd_adventure/data
    return os.path.normpath(os.path.join(data_dir, *parts))

def _load_json(path: str) -> Any:
    """Load a JSON file safely."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_races() -> List[Dict[str, Any]]:
    """Load race data from data/races.json cross-platform."""
    races_path = _data_path("races.json")
    return _load_json(races_path)

def generate_npcs(civilizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate NPCs for each civilization based on race data.
    Creates unique NPCs with random professions, traits, and roles.
    """
    races_data = load_races()
    npcs = []
    professions = ["Warrior", "Mage", "Hunter", "Merchant", "Scholar", "Farmer", "Priest", "Thief"]
    traits = ["Brave", "Cunning", "Kind", "Greedy", "Loyal", "Deceitful", "Curious", "Stoic"]

    for civ in civilizations:
        race_name = civ.get("race", "Human")
        race_info = next((r for r in races_data if r["name"].lower() == race_name.lower()), None)

        for _ in range(random.randint(5, 15)):  # Number of NPCs per civ
            npc = {
                "name": f"{race_name}_{random.randint(100, 999)}",
                "race": race_name,
                "profession": random.choice(professions),
                "trait": random.choice(traits),
                "home_civilization": civ["name"],
                "biome": civ.get("biome", "plains"),
                "is_notable": random.random() < 0.2,  # 20% chance of being notable
                "influence": random.randint(1, 100),
            }
            npcs.append(npc)

    return npcs

# ✅ Optional test runner for standalone use
if __name__ == "__main__":
    demo_civs = [
        {"name": "Dwarf Empire", "race": "Dwarf", "biome": "mountains"},
        {"name": "Elf Dominion", "race": "Elf", "biome": "forest"},
    ]
    demo_npcs = generate_npcs(demo_civs)
    print(json.dumps(demo_npcs[:5], indent=2))
