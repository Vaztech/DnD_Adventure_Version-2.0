# dnd_adventure/worldgen/civilization_generator.py
import os
import json
from typing import Dict, List, Any


def _data_path(*parts: str) -> str:
    """
    Build a normalized path to the data/ folder regardless of OS or install location.
    This file lives in: dnd_adventure/worldgen/civilization_generator.py
    data/ is a sibling of worldgen/, so we walk up one and into data/.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))          # .../dnd_adventure/worldgen
    project_pkg_dir = os.path.dirname(base_dir)                    # .../dnd_adventure
    data_dir = os.path.join(project_pkg_dir, "data")               # .../dnd_adventure/data
    return os.path.normpath(os.path.join(data_dir, *parts))        # handle slashes on Win/macOS/Linux


def _load_json(path: str) -> Any:
    """Load a JSON file with UTF-8 encoding, raising a clear error if missing/corrupt."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required data file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}") from e


def load_races() -> List[Dict[str, Any]]:
    """
    Load race definitions from data/races.json.
    Expected schema (minimal):
      [
        {
          "name": "Dwarf",
          "preferred_biome": "mountains",
          "description": "...",
          ...
        },
        ...
      ]
    """
    races_path = _data_path("races.json")
    return _load_json(races_path)


def generate_civilizations(biomes: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate lightweight civilization records using available race data and a biome map.

    Parameters
    ----------
    biomes : dict
        A biome map or metadata your pipeline already produced. At minimum, we use it
        to resolve a preferred biome token into a valid biome key. You can pass a simple
        dict like {"mountains": "mountains", "plains": "plains"} and expand later.

    Returns
    -------
    list of dict
        Example structure (you can extend fields freely):
        [
          {
            "name": "Dwarf Empire",
            "race": "Dwarf",
            "capital": {"x": 42, "y": 17},
            "biome": "mountains",
            "population": 2300,
            "traits": {"martial": 2, "arcane": 0, "commerce": 1},
          },
          ...
        ]
    """
    races_data = load_races()
    civs: List[Dict[str, Any]] = []

    # Simple deterministic-ish placement seed using race name length;
    # replace this with your world/coords allocator when ready.
    # We avoid random() here so results are stable for the same input set.
    x_cursor, y_cursor = 7, 11

    for race in races_data:
        race_name = race.get("name", "Unknown")
        pref_biome = str(race.get("preferred_biome", "plains")).lower()

        # Resolve to a key that exists in your biome set (fallback to 'plains')
        biome_key = pref_biome if pref_biome in biomes else "plains"

        # Very basic capital placement heuristic you can replace later
        x_cursor = (x_cursor * 37 + len(race_name) * 3) % 200
        y_cursor = (y_cursor * 29 + len(race_name) * 5) % 200
        capital = {"x": int(x_cursor), "y": int(y_cursor)}

        # A tiny flavor system you can expand (culture weights, etc.)
        traits = {
            "martial": max(0, min(3, (len(race_name) // 5) % 4)),
            "arcane": max(0, min(3, (len(race_name) // 3) % 4)),
            "commerce": max(0, min(3, (len(race_name) // 4) % 4)),
        }

        # Starter population heuristic (adjust/replace freely)
        population = 800 + (len(race_name) * 120)

        civs.append(
            {
                "name": f"{race_name} Empire",
                "race": race_name,
                "capital": capital,
                "biome": biome_key,
                "population": population,
                "traits": traits,
            }
        )

    return civs


# Optional: quick CLI check (does not change game behavior)
if __name__ == "__main__":
    # Minimal stand-in biomes map for local testing
    demo_biomes = {
        "plains": "plains",
        "forest": "forest",
        "mountains": "mountains",
        "desert": "desert",
        "swamp": "swamp",
        "tundra": "tundra",
        "hills": "hills",
        "coast": "coast",
    }
    civs = generate_civilizations(demo_biomes)
    print(json.dumps(civs, indent=2))
