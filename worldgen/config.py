"""
Worldgen configuration loader.

Reads dnd_adventure/data/worldgen.json if present, otherwise uses
sane defaults. This drives map size, biome thresholds, etc.
"""

import json
import logging
from .paths import data_path

logger = logging.getLogger(__name__)

DEFAULT_WORLDGEN_CFG = {
    "width": 64,
    "height": 48,
    "seed": 1337,
    "noise": {
        "scale": 32.0,
        "octaves": 4,
        "persistence": 0.5,
        "lacunarity": 2.0,
    },
    "biomes": {
        "water": 0.30,
        "sand":  0.36,
        "grass": 0.65,
        "forest":0.80,
    },
    "poi": {
        "towns": 6,
        "castles": 3,
        "dungeons": 6,
        "min_spacing": 4,
    },
    "rivers": 5,
}

def _read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"worldgen config not found at {path}, using defaults.")
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
    return default

def load_worldgen_cfg() -> dict:
    return _read_json(data_path("worldgen.json"), DEFAULT_WORLDGEN_CFG)
