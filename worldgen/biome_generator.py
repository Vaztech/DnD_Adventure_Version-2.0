# dnd_adventure/worldgen/biome_generator.py
"""
Biome generator

Provides a simple, robust generate_biomes(geography) function that works even if
the geography payload is minimal or missing. Returns a dict of biome keys your
other systems expect, so modules like civilization_generator and world_state
won't crash if a specific biome is referenced.
"""

from typing import Dict, Any

# Minimal resource flavors for each biome (expand later if you like)
_DEFAULT_BIOMES: Dict[str, Dict[str, Any]] = {
    "plains":   {"resources": ["grain", "herbs"], "climate": "temperate"},
    "forest":   {"resources": ["wood", "game"], "climate": "temperate"},
    "mountains":{"resources": ["ore", "stone"], "climate": "cold"},
    "desert":   {"resources": ["salt", "silica"], "climate": "arid"},
    "swamp":    {"resources": ["reeds", "peat"], "climate": "humid"},
    "tundra":   {"resources": ["fur", "ice"], "climate": "polar"},
    "hills":    {"resources": ["stone", "pasture"], "climate": "temperate"},
    "coast":    {"resources": ["fish", "salt"], "climate": "marine"},
}

def generate_biomes(geography: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Return a biome dictionary keyed by biome name.

    Parameters
    ----------
    geography : dict
        A structure from geography_generator.generate_geography(). This function
        does not require specific fields; if elevation/moisture maps are present,
        you can later map them to actual biome placement. For now, we return a
        normalized biome registry other systems can reference.

    Returns
    -------
    dict: {
      "plains":   {"resources": [...], "climate": "temperate"},
      "forest":   {...},
      ...
    }
    """
    # If you later add real maps in geography (e.g., heightmap, moisture),
    # compute distributions here and enrich each biome entry with locations.

    # For now, return a stable set of biome definitions so other systems
    # (civilizations, events, dialogue) can resolve biome keys safely.
    # Make a shallow copy so callers can mutate without affecting defaults.
    return {name: dict(info) for name, info in _DEFAULT_BIOMES.items()}
