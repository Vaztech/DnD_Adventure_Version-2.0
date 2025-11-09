# dnd_adventure/map_generator.py
# -----------------------------------------------------------------------------
# Compatibility wrapper for world generation.
#
# Why this file exists
# --------------------
# Older code (e.g. world.py) expects:
#
#     from dnd_adventure.map_generator import MapGenerator
#     mg = MapGenerator()
#     world = mg.generate_map()
#     name = mg.generate_name()
#
# We’ve refactored the real implementation into:
#
#     dnd_adventure/worldgen/map_generator.py
#
# which exposes:
#
#     from dnd_adventure.worldgen.map_generator import generate_map
#
# This file:
#   - Provides a stable import surface so legacy code keeps working.
#   - Delegates to the real implementation when available.
#   - Fails with a clear, explicit error if the implementation is missing.
#
# IMPORTANT:
#   - No recursion. This module NEVER calls itself.
#   - MapGenerator is ALWAYS defined so `from dnd_adventure.map_generator import
#     MapGenerator` will succeed as long as this file imports.
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
import random
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Internal reference to the real generate_map implementation.
# We resolve it lazily so import errors become clear and controlled.
_worldgen_generate_map = None


def _load_worldgen_impl() -> None:
    """
    Ensure _worldgen_generate_map is loaded from dnd_adventure.worldgen.map_generator.

    This is called the first time someone uses generate_map() or MapGenerator.
    If the implementation file is missing or broken, we raise a clean ImportError.

    This function NEVER calls anything in THIS file again, so no recursion.
    """
    global _worldgen_generate_map

    # Already loaded successfully once
    if _worldgen_generate_map is not None:
        return

    try:
        # Import the real generator from the worldgen package
        from dnd_adventure.worldgen.map_generator import generate_map as impl_generate_map
    except Exception as e:
        # Log a detailed error for debugging
        logger.error(
            "Failed to import dnd_adventure.worldgen.map_generator.generate_map: %s",
            e,
        )
        # Raise a clear ImportError so the caller understands what's wrong
        raise ImportError(
            "dnd_adventure.worldgen.map_generator.generate_map could not be imported. "
            "Check that 'dnd_adventure/worldgen/map_generator.py' exists, "
            "is error-free, and that 'dnd_adventure/worldgen/__init__.py' "
            "marks it as a package."
        ) from e

    # Cache the implementation so subsequent calls are instant
    _worldgen_generate_map = impl_generate_map


# -----------------------------------------------------------------------------
# Functional API (new code can use this directly)
# -----------------------------------------------------------------------------
def generate_map() -> Dict[str, Any]:
    """
    Generate a world map using the real implementation in worldgen.map_generator.

    New-style usage:
        from dnd_adventure.map_generator import generate_map
        world = generate_map()

    This wrapper:
      - Lazily loads the real implementation.
      - Raises a clear ImportError if worldgen is missing/broken.
    """
    _load_worldgen_impl()
    # At this point _worldgen_generate_map is a valid function
    return _worldgen_generate_map()


def generate_name(seed: int | None = None) -> str:
    """
    Lightweight deterministic-ish world name generator.

    Legacy code expects MapGenerator().generate_name(), so we expose both a
    function and a method (see class MapGenerator below).

    Behavior:
      - If seed is provided, we create a local Random with that seed.
      - If not, we use global random for variety.
    """
    rng = random.Random(seed) if seed is not None else random

    prefixes = [
        "Elder", "Shadow", "Mythic", "Iron", "Crystal",
        "Dawn", "Obsidian", "Silver", "Ember", "Storm",
    ]
    middles = [
        "fall", "wind", "vale", "crest", "reach",
        "moor", "deep", "light", "guard", "spire",
    ]
    suffixes = [
        "", "", "",           # weight toward two-part names
        " Realms", " Isles", " Lands", " Expanse", " Frontier",
    ]

    name = rng.choice(prefixes) + rng.choice(middles) + rng.choice(suffixes)
    # Clean up any accidental double spaces
    return " ".join(name.split())


# -----------------------------------------------------------------------------
# Class-based API (backwards compatible with old code)
# -----------------------------------------------------------------------------
class MapGenerator:
    """
    Backwards-compatible façade.

    Older code does:
        from dnd_adventure.map_generator import MapGenerator
        mg = MapGenerator()
        world = mg.generate_map()
        name = mg.generate_name()

    This class keeps that working by:
      - Delegating generate_map() to the real implementation.
      - Using the shared generate_name() helper.

    NOTE:
      - __init__ accepts *args/**kwargs for compatibility but ignores them.
      - No configuration stored here; everything is driven by worldgen/data.
    """

    def __init__(self, *args, **kwargs) -> None:
        logger.debug(
            "MapGenerator initialized (compat wrapper) with args=%s kwargs=%s",
            args,
            kwargs,
        )

    def generate_map(self) -> Dict[str, Any]:
        """
        Instance method wrapper for world generation.

        Returns:
            Dict representing the generated world. Structure is defined by
            dnd_adventure.worldgen.map_generator.generate_map().
        """
        return generate_map()

    def generate_name(self, seed: int | None = None) -> str:
        """
        Instance method wrapper for name generation.

        Returns:
            A flavor world name string.
        """
        return generate_name(seed)
