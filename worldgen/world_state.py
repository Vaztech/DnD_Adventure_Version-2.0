# dnd_adventure/worldgen/world_state.py
# -----------------------------------------------------------------------------
# WorldState
#
# This module owns the in-memory representation of the generated world and
# provides a single, stable shape that the rest of the game can rely on.
#
# IMPORTANT:
# - Game / GameWorld expect attributes like:
#       world_state.geography
#       world_state.biomes
#       world_state.civilizations
#       world_state.events
#       world_state.npcs
#       world_state.timeline
#       world_state.dialogue
#       world_state.civ_changes
#
#   Those MUST exist even if generation fails or has not yet run.
#
# - Older code may instantiate this as WorldState(world_name, base_dir)
#   Newer code (your current GameWorld) calls WorldState() with no args.
#   This implementation supports BOTH styles.
#
# - Actual heavy lifting is delegated to other modules in worldgen/:
#       geography_generator, biome_generator, civilization_generator,
#       event_simulator, npc_simulator, timeline_manager, dialogue_generator
#
# - This file also verifies critical data files (races.json, graphics.json)
#   live in dnd_adventure/data/, and will create safe defaults if missing.
#   That keeps startup robust on all OSes.
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Filenames we care about inside the shared data directory
DATA_FILES = {
    "races": "races.json",
    "graphics": "graphics.json",
}


# -----------------------------------------------------------------------------
# Helper: resolve package-level data directory
# -----------------------------------------------------------------------------
def _pkg_root() -> str:
    """
    Return absolute path to the dnd_adventure package root.

    This file lives at:
        dnd_adventure/worldgen/world_state.py
    So the package root is two levels up.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir, os.pardir))


def _data_dir() -> str:
    """Return the path to dnd_adventure/data (created if missing)."""
    path = os.path.join(_pkg_root(), "data")
    os.makedirs(path, exist_ok=True)
    return path


# -----------------------------------------------------------------------------
# Helper: verify / create essential data files
# -----------------------------------------------------------------------------
def verify_data_files() -> None:
    """
    Ensure essential JSON data files exist in dnd_adventure/data.

    This keeps the game from crashing when races.json or graphics.json
    are missing in a fresh install or release archive.

    Behavior:
      - If races.json is missing, we write a small default set.
      - If graphics.json is missing, we write simple ASCII/colour defaults.
    """
    data_dir = _data_dir()

    # --- races.json ---------------------------------------------------------
    races_path = os.path.join(data_dir, DATA_FILES["races"])
    if not os.path.exists(races_path):
        logger.warning("Missing %s — creating default races.json.", races_path)
        default_races = [
            {
                "name": "Human",
                "description": "Adaptable and ambitious.",
                "ability_modifiers": {},
                "subraces": {},
            },
            {
                "name": "Elf",
                "description": "Graceful and wise.",
                "ability_modifiers": {"Dexterity": 2},
                "subraces": {
                    "High Elf": {
                        "description": "Scholarly elves with keen minds.",
                        "ability_modifiers": {"Intelligence": 1},
                    },
                    "Wood Elf": {
                        "description": "Stealthy elves tied to forests.",
                        "ability_modifiers": {"Wisdom": 1},
                    },
                },
            },
            {
                "name": "Dwarf",
                "description": "Stout and hardy.",
                "ability_modifiers": {"Constitution": 2},
                "subraces": {
                    "Hill Dwarf": {
                        "description": "Stalwart dwarves of the hills.",
                        "ability_modifiers": {"Wisdom": 1},
                    },
                    "Mountain Dwarf": {
                        "description": "Strong dwarves of the mountains.",
                        "ability_modifiers": {"Strength": 1},
                    },
                },
            },
        ]
        try:
            with open(races_path, "w", encoding="utf-8") as f:
                json.dump(default_races, f, indent=2)
        except OSError as e:
            logger.error("Failed to create default races.json: %s", e)

    # --- graphics.json ------------------------------------------------------
    graphics_path = os.path.join(data_dir, DATA_FILES["graphics"])
    if not os.path.exists(graphics_path):
        logger.warning("Missing %s — creating default graphics.json.", graphics_path)
        default_graphics = {
            "tiles": {
                "water": "~",
                "sand": ".",
                "grass": ".",
                "forest": "T",
                "mountain": "^",
                "river": "~",
                "road": "#",
            },
            "colors": {
                "water": "blue",
                "sand": "yellow",
                "grass": "green",
                "forest": "green",
                "mountain": "white",
            },
        }
        try:
            with open(graphics_path, "w", encoding="utf-8") as f:
                json.dump(default_graphics, f, indent=2)
        except OSError as e:
            logger.error("Failed to create default graphics.json: %s", e)


# -----------------------------------------------------------------------------
# WorldState class
# -----------------------------------------------------------------------------
class WorldState:
    """
    Container for all generated world data.

    This class is designed to be:

      - Safe: all expected attributes exist immediately after __init__,
        so other systems never crash with AttributeError.
      - Flexible: can be constructed old-style:
            WorldState("MyWorld", "/some/path")
        or new-style:
            WorldState()
      - Pluggable: uses helper modules in worldgen/ to actually populate
        geography, biomes, civilizations, events, npcs, etc.
    """

    def __init__(self,
                 world_name: Optional[str] = None,
                 base_dir: Optional[str] = None) -> None:
        # Name is purely cosmetic; used for logging / file naming by callers.
        self.world_name: str = world_name or "generated_world"

        # Base directory for any file IO by callers (not heavily used here);
        # default to package root so this is always valid.
        self.base_dir: str = base_dir or _pkg_root()

        # Make sure required game data exists before we do any generation.
        verify_data_files()

        # ------------------------------------------------------------------
        # Core attributes expected throughout the codebase.
        # These are initialized to safe empty values RIGHT AWAY so that even
        # if generation fails, GameWorld / Game can still reference them.
        # ------------------------------------------------------------------
        self.geography: List[List[float]] = []
        self.biomes: List[List[str]] = []
        self.civilizations: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.npcs: List[Dict[str, Any]] = []
        self.timeline: Dict[int, List[str]] = {}
        self.dialogue: List[str] = []
        self.civ_changes: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # Generation pipeline
    # -------------------------------------------------------------------------
    def generate(self) -> None:
        """
        Run the full world-generation pipeline.

        Populates all public attributes in-place.

        This method is safe to call multiple times; it simply overwrites
        the current data with a fresh generation using the helper modules.
        """
        logger.info("Generating WorldState for '%s'...", self.world_name)

        # Lazy imports keep this file lightweight and avoid circular imports.
        try:
            from .geography_generator import generate_geography
            from .biome_generator import generate_biomes
            from .civilization_generator import generate_civilizations
            from .event_simulator import simulate_events
            from .npc_simulator import generate_npcs
            from .timeline_manager import record_timeline
            from .dialogue_generator import generate_dialogue
        except Exception as e:
            logger.error("Failed to import worldgen components: %s", e, exc_info=True)
            # Leave attributes as their safe defaults and bail out.
            return

        try:
            # 1) Base geography (heightmap, regions, etc.)
            self.geography = generate_geography()

            # 2) Biome layout from geography
            self.biomes = generate_biomes(self.geography)

            # 3) Civilizations seeded into the world
            self.civilizations = generate_civilizations(self.biomes)

            # 4) Historical events among civilizations
            self.events = simulate_events(self.civilizations)

            # 5) NPCs tied into civs/regions
            self.npcs = generate_npcs(self.civilizations)

            # 6) Dialogue lines based on NPCs / events
            self.dialogue = generate_dialogue(self.npcs, self.events) \
                if _accepts_events(generate_dialogue) \
                else generate_dialogue(self.npcs)

            # 7) Timeline index by year -> list of event summaries
            self.timeline = record_timeline(self.events)

            # 8) Civ change tracker (for future dynamic updates)
            self.civ_changes = []
            for civ in self.civilizations:
                self.civ_changes.append({
                    "name": civ.get("name", "Unknown"),
                    "race": civ.get("race"),
                    "subrace": civ.get("subrace"),
                    "power_change": 0,
                    "population_change": 0,
                })

            logger.info("World generation complete for '%s'.", self.world_name)

        except Exception as e:
            # If any stage fails, log and keep safe defaults so callers do not die.
            logger.error("Error during world generation for '%s': %s",
                         self.world_name, e, exc_info=True)
            # Attributes remain as previously set (either defaults or partial).


# -----------------------------------------------------------------------------
# Small helper: detect generate_dialogue signature flexibly
# -----------------------------------------------------------------------------
def _accepts_events(func) -> bool:
    """
    Return True if generate_dialogue(func) appears to accept 2 params
    (npcs, events). This lets us support both of your versions without
    breaking either.
    """
    try:
        from inspect import signature
        params = signature(func).parameters
        return len(params) >= 2
    except Exception:
        return False
