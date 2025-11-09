"""
dnd_adventure/world.py
----------------------

World
=====

This module owns the *runtime view* of the overworld:

- Talks to `dnd_adventure.map_generator` (which in turn delegates to
  `worldgen.map_generator`) to generate or load a deterministic world map.
- Wraps the raw map data (heightmap, biomes, POIs, roads, etc.) behind a
  simple API used by the rest of the game:
    - get_location(...)
    - get_tile_symbol(...)
    - display_map(...)
- Provides light narrative helpers (random-ish names, eras, events) so
  your original flavor is preserved without depending on old methods like
  `MapGenerator.generate_name()` that no longer exist.

Key design goals:
- **No breaking changes** for Game/UI code that expects a `World` object.
- **No Windows-only paths** – everything is OS-agnostic.
- **Zero dependency on private methods** from the refactored map generator.

This file is intentionally self-contained and well-commented per your request.
"""

from __future__ import annotations

import logging
import random
from typing import Dict, Tuple, Optional, List

from colorama import Fore, Style

# ---------------------------------------------------------------------------
# We use the compatibility wrapper you showed earlier:
#   dnd_adventure/map_generator.py
# That wrapper:
#   - Imports worldgen.map_generator.generate_map
#   - Exposes:
#         def generate_map()
#         class MapGenerator: generate_map(self)
#   - Does NOT expose generate_name() or load_or_generate_map().
# ---------------------------------------------------------------------------
from dnd_adventure.map_generator import MapGenerator

logger = logging.getLogger(__name__)


class World:
    """
    High-level world container used by Game/UI.

    Responsibilities:
    - Own a single world seed.
    - Call MapGenerator().generate_map() to get the terrain + POIs.
    - Provide helpers to:
        * resolve tile/POI info at (x, y)
        * render a local view around the player
        * (optionally) expose some generated lore hooks

    Shape of `self.map` (from the refactored generator):

        {
          "width": int,
          "height": int,
          "seed": int,
          "height": [[float]],
          "biomes": [[str]],
          "rivers": [[bool]],
          "roads": [[bool]],
          "locations": {
            "x,y": {"type": "town|castle|dungeon", "name": str}
          }
        }
    """

    # ----------------------------------------------------------------------
    # Construction
    # ----------------------------------------------------------------------
    def __init__(self, seed: Optional[int] = None, graphics: Optional[Dict] = None):
        """
        Create a new World instance.

        :param seed:
            Optional explicit RNG seed.
            - If provided, worldgen is deterministic across runs.
            - If None, a random seed is chosen and stored.
        :param graphics:
            Optional mapping from biome/type -> display symbol.
            - Used only for ASCII rendering in display_map().
            - If None, we fall back to safe defaults.
        """
        logger.debug("Initializing World...")

        # Use a fixed seed if given, else roll one.
        self.seed: int = seed if seed is not None else random.randint(1, 999_999)

        # Attach graphics mapping (for map display).
        # You can wire this to data/graphics.json higher up in Game if desired.
        self.graphics: Dict = graphics or {}

        # Create a MapGenerator wrapper.
        # NOTE: Our compatibility MapGenerator ignores args, but we pass the seed
        #       anyway so old signatures are harmlessly supported.
        self.map_generator = MapGenerator(self.seed)

        # Ask the generator for the full world data dict.
        # This is the *only* call we rely on from MapGenerator.
        world_data = self.map_generator.generate_map()
        if not isinstance(world_data, dict):
            raise ValueError("MapGenerator.generate_map() did not return a dict")

        # Store core map fields with safe fallbacks.
        self.map: Dict = world_data
        self.width: int = int(world_data.get("width", 0))
        self.height: int = int(world_data.get("height", 0))
        self.locations: Dict[str, Dict] = world_data.get("locations", {})

        # Give the world a simple name. If your generator ever adds one,
        # we pick that up; otherwise a seed-based label.
        self.name: str = world_data.get("name", f"World-{self.seed}")

        logger.info(f"World initialized: {self.name} ({self.width}x{self.height}, seed={self.seed})")

        # Generate a lightweight historical timeline for flavor text.
        # This replaces old calls to MapGenerator.generate_name().
        self.timeline: List[Dict] = self._generate_timeline()

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _random_name(self) -> str:
        """
        Very small, self-contained random name generator.

        We add this because the old code called MapGenerator.generate_name(),
        which no longer exists in the refactored pipeline. Using this local
        helper keeps your timeline / lore features alive without new deps.
        """
        syllables = [
            "al", "an", "ar", "bal", "bel", "cor", "dor", "drim",
            "el", "far", "gal", "hal", "kel", "lor", "mir", "nar",
            "or", "rim", "sar", "thal", "ur", "vel"
        ]
        length = random.randint(2, 4)
        return "".join(random.choice(syllables).capitalize() for _ in range(length))

    def _generate_timeline(self) -> List[Dict]:
        """
        Generate a simple, lore-friendly timeline of eras and events.

        This mirrors the *spirit* of your original implementation:
        - 3–5 eras
        - each with a random length and 2–5 notable events
        - names/places built from `_random_name()`

        The data is stored on self.timeline for any UI that wants to display it.
        """
        logger.debug("Generating world timeline for flavor...")
        timeline: List[Dict] = []

        if self.width <= 0 or self.height <= 0:
            # If map failed or is empty, don't try to be fancy.
            logger.warning("World map dimensions invalid; skipping timeline generation.")
            return timeline

        num_eras = random.randint(3, 5)
        current_year = 0

        for i in range(num_eras):
            era_length = random.randint(80, 300)
            era_name = f"Era of {self._random_name()}"
            era = {
                "name": era_name,
                "start_year": current_year,
                "events": []
            }

            num_events = random.randint(2, 5)
            for _ in range(num_events):
                event_year = current_year + random.randint(0, era_length)
                kingdom_a = self._random_name()
                kingdom_b = self._random_name()
                artifact = f"{self._random_name()} Stone"
                event_desc = random.choice([
                    f"The kingdom of {kingdom_a} is founded by a wandering hero.",
                    f"A great war erupts between {kingdom_a} and {kingdom_b}.",
                    f"An ancient artifact known as the {artifact} is unearthed.",
                    f"The skies darken for a decade over the lands of {kingdom_a}.",
                    f"A golden age of trade flourishes along the old roads of {kingdom_a}."
                ])
                era["events"].append({
                    "year": event_year,
                    "description": event_desc
                })

            timeline.append(era)
            current_year += era_length + 1

        logger.debug("World timeline generation complete.")
        return timeline

    # ----------------------------------------------------------------------
    # Location helpers
    # ----------------------------------------------------------------------
    def get_location(self, x: int, y: int) -> Dict:
        """
        Return a dict describing the location at (x, y).

        Priority:
        1. If a POI exists in self.locations, return that info.
        2. Otherwise derive a basic terrain record from the biome map.

        This ensures calls like Game/UI asking for tiles never crash
        when there is no explicit POI entry at that coordinate.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return {"x": x, "y": y, "type": "void", "name": None}

        key = f"{x},{y}"
        if key in self.locations:
            loc = dict(self.locations[key])
            loc.setdefault("x", x)
            loc.setdefault("y", y)
            return loc

        # Fallback: infer from biome.
        biome = self.map.get("biomes", [[ "grass" ]])[y][x]
        terrain_type = {
            "water": "water",
            "sand": "sand",
            "grass": "plains",
            "forest": "forest",
            "mountain": "mountain",
        }.get(biome, "plains")

        return {
            "x": x,
            "y": y,
            "type": terrain_type,
            "name": None
        }

    # ----------------------------------------------------------------------
    # Display helpers (used by UI / Game to render the minimap)
    # ----------------------------------------------------------------------
    def _symbol_for(self, loc: Dict, is_player: bool = False) -> str:
        """
        Choose a single-character symbol for a tile, using (in order):

        - Player indicator '@' if `is_player` is True.
        - Explicit POI type: dungeon/town/castle.
        - Biome-based fallback using graphics.json mappings if provided.
        - A generic '.' as the final safety net.
        """
        if is_player:
            return Fore.RED + "@" + Style.RESET_ALL

        t = loc.get("type", "plains")

        # Explicit POI types first
        if t == "dungeon":
            return Fore.MAGENTA + "D" + Style.RESET_ALL
        if t == "castle":
            return Fore.YELLOW + "C" + Style.RESET_ALL
        if t == "town":
            return Fore.CYAN + "T" + Style.RESET_ALL

        # Look up biome from map if available
        x, y = loc.get("x", 0), loc.get("y", 0)
        biome = None
        try:
            biome = self.map.get("biomes", [[]])[y][x]
        except Exception:
            biome = None

        # Try graphics.json-style tiles mapping if passed in
        tiles = self.graphics.get("tiles", {})
        if biome and biome in tiles:
            return tiles[biome]

        # Fallback defaults by biome/type
        if biome == "water":
            return Fore.BLUE + "~" + Style.RESET_ALL
        if biome == "sand":
            return Fore.YELLOW + "." + Style.RESET_ALL
        if biome == "forest":
            return Fore.GREEN + "♣" + Style.RESET_ALL
        if biome == "mountain":
            return Fore.WHITE + "^" + Style.RESET_ALL

        # Generic ground
        return "."  # intentionally plain; safe in all terminals

    def display_map(self, player_pos: Tuple[int, int]) -> str:
        """
        Build a small ASCII map window centered on the player.

        - Shows a square (radius 5) around player_pos.
        - Uses `_symbol_for(...)` for each tile.
        - Returns the full string so UIManager can print it cleanly.

        This replaces any direct printing inside World so that the caller
        controls when/where it is displayed.
        """
        if self.width <= 0 or self.height <= 0:
            return "[World map unavailable]"

        px, py = player_pos
        view_radius = 5
        lines: List[str] = []

        for dy in range(view_radius, -view_radius - 1, -1):
            row_chars: List[str] = []
            for dx in range(-view_radius, view_radius + 1):
                x = px + dx
                y = py + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    loc = self.get_location(x, y)
                    is_player = (x, y) == (px, py)
                    row_chars.append(self._symbol_for(loc, is_player=is_player))
                else:
                    # Outside world bounds
                    row_chars.append(" ")
            lines.append("".join(row_chars))

        return "\n".join(lines)
