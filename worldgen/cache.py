"""
Pickle-based cache for generated maps (per seed + size).
"""

import os
import pickle
import logging
from typing import Optional, Dict
from .paths import data_path, ensure_dir

logger = logging.getLogger(__name__)

def cache_dir() -> str:
    path = data_path("cache")
    ensure_dir(path)
    return path

def cache_path(seed: int, W: int, H: int) -> str:
    return os.path.join(cache_dir(), f"map_cache_seed{seed}_{W}x{H}.pkl")

def load_from_cache(seed: int, W: int, H: int) -> Optional[Dict]:
    path = cache_path(seed, W, H)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)
        logger.info(f"Loaded world map from cache: {path}")
        return data
    except Exception as e:
        logger.warning(f"Failed to load cache {path}: {e}")
        return None

def save_to_cache(seed: int, W: int, H: int, world: Dict) -> None:
    path = cache_path(seed, W, H)
    try:
        with open(path, "wb") as f:
            pickle.dump(world, f)
        logger.info(f"World map cached: {path}")
    except Exception as e:
        logger.warning(f"Failed to write cache {path}: {e}")
