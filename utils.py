# dnd_adventure/utils.py
# -----------------------------------------------------------------------------
# Utility helpers for robust, cross-platform file access and small IO helpers.
# Key changes:
#   • Added get_package_root() so other modules can reliably resolve paths
#   • get_graphics_config() now prefers data/graphics.json, then falls back
#     to resources/graphics.json, and will auto-create a sane default if missing
#   • All file IO uses UTF-8 and os.path for portability
# -----------------------------------------------------------------------------

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Path helpers
# -----------------------------------------------------------------------------
def get_package_root() -> str:
    """Return the absolute path to the dnd_adventure package directory.
    This works no matter where the game is launched from.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    # __file__ points at dnd_adventure/utils.py, so its parent is the package
    return os.path.abspath(here)


def get_resource_path(*parts: str) -> str:
    """Join parts under the package root in a cross-platform way."""
    return os.path.join(get_package_root(), *parts)


def ensure_dir(path: str) -> None:
    """Create a directory if it doesn't already exist."""
    os.makedirs(path, exist_ok=True)


# -----------------------------------------------------------------------------
# JSON helpers
# -----------------------------------------------------------------------------
def read_json(path: str, default: Any = None) -> Any:
    """Read JSON with UTF-8 encoding; return default on any error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read JSON {path}: {e}. Using default.")
        return default


def write_json(path: str, data: Any) -> None:
    """Write JSON with UTF-8 encoding; create parent dir as needed."""
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# -----------------------------------------------------------------------------
# Graphics configuration loader
# -----------------------------------------------------------------------------
_DEFAULT_GRAPHICS = {
    "tiles": {"grass": ".", "mountain": "^", "forest": "T", "water": "~", "desert": "*"},
    "colors": {"grass": "green", "mountain": "gray", "forest": "darkgreen", "water": "blue", "desert": "yellow"},
}


def get_graphics_config() -> Dict[str, Any]:
    """Load graphics.json, preferring data/ then resources/ with a safe fallback.

    Search order (first hit wins):
      1) dnd_adventure/data/graphics.json
      2) dnd_adventure/resources/graphics.json
      3) Auto-create data/graphics.json with _DEFAULT_GRAPHICS and use it
    """
    data_path = get_resource_path("data", "graphics.json")
    res_path = get_resource_path("resources", "graphics.json")  # legacy location

    # Prefer data/graphics.json if it exists
    if os.path.exists(data_path):
        cfg = read_json(data_path, _DEFAULT_GRAPHICS)
        if cfg is None:
            cfg = _DEFAULT_GRAPHICS
        return cfg

    # Fallback to resources/graphics.json if present
    if os.path.exists(res_path):
        cfg = read_json(res_path, _DEFAULT_GRAPHICS)
        # Also mirror a copy into data/ so future code has a stable location
        try:
            write_json(data_path, cfg)
        except Exception as e:
            logger.debug(f"Could not mirror graphics.json to data/: {e}")
        return cfg

    # Neither exists — create data/graphics.json from defaults
    logger.warning("graphics.json not found in data/ or resources/. Creating default in data/.")
    write_json(data_path, _DEFAULT_GRAPHICS)
    return _DEFAULT_GRAPHICS


# Backwards-compat helper some modules still call
def load_graphics() -> Dict[str, Any]:
    """Alias kept for older code paths."""
    return get_graphics_config()
