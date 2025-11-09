"""
dnd_adventure.worldgen.map_generator
------------------------------------

Core world generation logic for DnD Adventure.

This module is the "real" map generator used by:
    dnd_adventure/map_generator.py    (compat wrapper)
    dnd_adventure/world.py
    dnd_adventure/game_world.py

Design goals:
- Cross-platform, no OS-specific hacks.
- No heavy external deps; uses simple value-noise + FBM.
- Configurable via dnd_adventure/data/worldgen.json (optional).
- Robust: missing/partial config falls back to safe defaults.
- Produces a world dict shaped like:

    {
        "width": int,
        "height": int,
        "seed": int,
        "heightmap": [[float]],        # normalized 0..1
        "biomes":  [[str]],            # "water"/"sand"/"grass"/"forest"/"mountain"
        "rivers":  [[bool]],
        "roads":   [[bool]],
        "locations": {
            "x,y": { "type": "town|castle|dungeon", "name": str },
            ...
        }
    }

The wrapper at dnd_adventure/map_generator.py provides:
    - MapGenerator().generate_map()
    - MapGenerator().generate_name()

So legacy code keeps working without knowing about this file.
"""

from __future__ import annotations

import json
import logging
import math
import os
import pickle
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# PATH HELPERS
# =============================================================================


def _normalize_world_dict(world: dict) -> dict:
    """
    Normalize world dict shape for backwards compatibility.

    Old bug:
      - "height" key was overwritten with the 2D heightmap list.
      - World.__init__ expects:
            width:  int
            height: int
        not a list.

    This function:
      - If world["height"] is a 2D list, treats it as a heightmap.
      - Moves that to world["heightmap"].
      - Restores scalar width/height based on that array.
    """
    if not isinstance(world, dict):
        return world

    h_val = world.get("height")

    # Detect old format where "height" is actually the heightmap 2D list
    if isinstance(h_val, list) and h_val and isinstance(h_val[0], list):
        heightmap = h_val
        H = len(heightmap)
        W = len(heightmap[0]) if H > 0 else 0

        # Store proper fields
        world["heightmap"] = heightmap
        world["height"] = H

        # Only fix width if it's missing or wrong
        if not isinstance(world.get("width"), int):
            world["width"] = W

    return world


def _pkg_root() -> str:
    """Resolve absolute path to the dnd_adventure package root."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))


def _data_path(*parts: str) -> str:
    """Build a path under dnd_adventure/data using OS-safe joins."""
    return os.path.join(_pkg_root(), "data", *parts)


def _ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist (no error if it does)."""
    os.makedirs(path, exist_ok=True)


def _read_json(path: str, default):
    """Safe JSON loader – returns default on missing/invalid file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Missing {path} — using defaults.")
        return default
    except Exception as e:
        logger.error(f"Failed to read {path}: {e} — using defaults.")
        return default


def _write_json(path: str, obj) -> None:
    """Safe JSON writer for debug/export helpers."""
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


# =============================================================================
# WORLDGEN CONFIGURATION
# =============================================================================

_DEFAULT_WORLDGEN_CFG = {
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
        "sand": 0.36,
        "grass": 0.65,
        "forest": 0.80,
    },
    "poi": {
        "towns": 6,
        "castles": 3,
        "dungeons": 6,
        "min_spacing": 4,
    },
    "rivers": 5,
}


def _load_worldgen_cfg() -> dict:
    """Load data/worldgen.json or return defaults."""
    return _read_json(_data_path("worldgen.json"), _DEFAULT_WORLDGEN_CFG)


def _normalize_biome_thresholds(th: dict) -> dict:
    """
    Guarantee a complete, ordered set of biome thresholds.
    """
    base = dict(_DEFAULT_WORLDGEN_CFG["biomes"])

    if isinstance(th, dict):
        for k in ("water", "sand", "grass", "forest"):
            if k in th:
                try:
                    base[k] = float(th[k])
                except (TypeError, ValueError):
                    logger.warning(f"Invalid biome threshold for {k}: {th[k]} — using default.")

    order = ["water", "sand", "grass", "forest"]
    last = 0.0
    for key in order:
        v = max(0.0, min(1.0, base[key]))
        if v < last:
            v = min(1.0, last + 0.01)
        base[key] = v
        last = v

    return base


# =============================================================================
# NOISE FUNCTIONS (VALUE NOISE + FBM)
# =============================================================================


def _hash2i(x: int, y: int, seed: int) -> int:
    """Deterministic 2D hash -> 32-bit int."""
    n = (x * 0x1F1F1F1F) ^ (y * 0x5F356495) ^ seed
    n ^= n >> 13
    n *= 0x85EBCA6B
    n ^= n >> 16
    return n & 0xFFFFFFFF


def _rand01_from_hash(h: int) -> float:
    return (h % 1000003) / 1000003.0


def _value_at_int_lattice(ix: int, iy: int, seed: int) -> float:
    return _rand01_from_hash(_hash2i(ix, iy, seed))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def _value_noise2d(x: float, y: float, seed: int) -> float:
    ix = int(math.floor(x))
    iy = int(math.floor(y))
    fx = x - ix
    fy = y - iy

    v00 = _value_at_int_lattice(ix, iy, seed)
    v10 = _value_at_int_lattice(ix + 1, iy, seed)
    v01 = _value_at_int_lattice(ix, iy + 1, seed)
    v11 = _value_at_int_lattice(ix + 1, iy + 1, seed)

    sx = _smoothstep(fx)
    sy = _smoothstep(fy)

    ix0 = _lerp(v00, v10, sx)
    ix1 = _lerp(v01, v11, sx)

    return _lerp(ix0, ix1, sy)


def _fbm(
    x: float,
    y: float,
    seed: int,
    octaves: int,
    persistence: float,
    lacunarity: float,
) -> float:
    amp = 1.0
    freq = 1.0
    total = 0.0
    norm = 0.0

    for _ in range(octaves):
        total += _value_noise2d(x * freq, y * freq, seed) * amp
        norm += amp
        amp *= persistence
        freq *= lacunarity

    return total / max(norm, 1e-9)


# =============================================================================
# HEIGHTMAP + BIOMES
# =============================================================================


def _heightmap(width: int, height: int, seed: int, noise_cfg: dict) -> List[List[float]]:
    scale = max(1e-6, float(noise_cfg.get("scale", 32.0)))
    octaves = int(noise_cfg.get("octaves", 4))
    persistence = float(noise_cfg.get("persistence", 0.5))
    lacunarity = float(noise_cfg.get("lacunarity", 2.0))

    hm = [[0.0 for _ in range(width)] for _ in range(height)]

    for j in range(height):
        for i in range(width):
            x = (i + 1000) / scale
            y = (j + 1000) / scale
            hm[j][i] = _fbm(x, y, seed, octaves, persistence, lacunarity)

    lo = min(min(row) for row in hm)
    hi = max(max(row) for row in hm)
    rng = max(hi - lo, 1e-9)

    for j in range(height):
        for i in range(width):
            hm[j][i] = (hm[j][i] - lo) / rng

    return hm


def _biome_from_height(h: float, th: dict) -> str:
    water = float(th.get("water", _DEFAULT_WORLDGEN_CFG["biomes"]["water"]))
    sand = float(th.get("sand", _DEFAULT_WORLDGEN_CFG["biomes"]["sand"]))
    grass = float(th.get("grass", _DEFAULT_WORLDGEN_CFG["biomes"]["grass"]))
    forest = float(th.get("forest", _DEFAULT_WORLDGEN_CFG["biomes"]["forest"]))

    if h < water:
        return "water"
    if h < sand:
        return "sand"
    if h < grass:
        return "grass"
    if h < forest:
        return "forest"
    return "mountain"


def _biomemap(hm: List[List[float]], thresholds: dict) -> List[List[str]]:
    H = len(hm)
    W = len(hm[0]) if H else 0
    bm = [["grass"] * W for _ in range(H)]

    for j in range(H):
        for i in range(W):
            bm[j][i] = _biome_from_height(hm[j][i], thresholds)

    return bm


# =============================================================================
# RIVERS
# =============================================================================


def _neighbors(i: int, j: int, W: int, H: int) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        x, y = i + di, j + dj
        if 0 <= x < W and 0 <= y < H:
            out.append((x, y))
    return out


def _find_local_peaks(hm: List[List[float]], count: int) -> List[Tuple[int, int]]:
    H = len(hm)
    W = len(hm[0]) if H else 0
    candidates = []

    for j in range(H):
        for i in range(W):
            h = hm[j][i]
            if all(h >= hm[y][x] for (x, y) in _neighbors(i, j, W, H)):
                candidates.append((i, j, h))

    candidates.sort(key=lambda t: t[2], reverse=True)
    return [(i, j) for (i, j, _) in candidates[:count]]


def _carve_rivers(
    hm: List[List[float]],
    bm: List[List[str]],
    river_count: int,
) -> List[List[bool]]:
    H = len(hm)
    W = len(hm[0]) if H else 0
    rivers = [[False] * W for _ in range(H)]

    sources = _find_local_peaks(hm, river_count)

    for sx, sy in sources:
        i, j = sx, sy
        visited = set()

        for _ in range(W * H * 2):
            visited.add((i, j))
            rivers[j][i] = True

            if (
                bm[j][i] == "water"
                or i == 0
                or j == 0
                or i == W - 1
                or j == H - 1
            ):
                break

            neigh = _neighbors(i, j, W, H)
            neigh.sort(key=lambda xy: hm[xy[1]][xy[0]])

            moved = False
            for nx, ny in neigh:
                if (nx, ny) in visited:
                    continue
                if hm[ny][nx] <= hm[j][i] + 0.01:
                    i, j = nx, ny
                    moved = True
                    break

            if not moved:
                i, j = neigh[0]

    for j in range(H):
        for i in range(W):
            if rivers[j][i]:
                bm[j][i] = "water"

    return rivers


# =============================================================================
# POIs + ROADS
# =============================================================================


@dataclass
class POI:
    x: int
    y: int
    type: str  # 'town' | 'castle' | 'dungeon'


def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _place_pois(
    bm: List[List[str]],
    counts: Dict[str, int],
    min_spacing: int,
    rng: random.Random,
) -> List[POI]:
    H = len(bm)
    W = len(bm[0]) if H else 0
    pois: List[POI] = []

    def try_place(kind: str, tries: int = 4000) -> bool:
        for _ in range(tries):
            i = rng.randrange(W)
            j = rng.randrange(H)
            biome = bm[j][i]

            if kind in ("town", "castle"):
                if biome not in ("grass", "forest"):
                    continue
            elif kind == "dungeon":
                if biome not in ("mountain", "forest", "grass"):
                    continue

            if any(_manhattan((p.x, p.y), (i, j)) < min_spacing for p in pois):
                continue

            pois.append(POI(i, j, kind))
            return True
        return False

    for _ in range(counts.get("castles", 0)):
        try_place("castle")
    for _ in range(counts.get("towns", 0)):
        try_place("town")
    for _ in range(counts.get("dungeons", 0)):
        try_place("dungeon")

    return pois


def _pass_cost(biome: str) -> int:
    return {
        "water": 9999,
        "sand": 6,
        "grass": 3,
        "forest": 5,
        "mountain": 8,
    }.get(biome, 4)


def _lay_road(
    bm: List[List[str]],
    roads: List[List[bool]],
    a: Tuple[int, int],
    b: Tuple[int, int],
) -> None:
    H = len(bm)
    W = len(bm[0]) if H else 0
    x, y = a
    tx, ty = b
    steps = 0
    max_steps = W * H

    while (x, y) != (tx, ty) and steps < max_steps:
        steps += 1
        candidates = _neighbors(x, y, W, H)
        candidates.sort(
            key=lambda xy: (
                _pass_cost(bm[xy[1]][xy[0]]),
                _manhattan(xy, (tx, ty)),
            )
        )

        moved = False
        for nx, ny in candidates:
            if bm[ny][nx] == "water":
                continue
            x, y = nx, ny
            roads[ny][nx] = True
            moved = True
            break

        if not moved:
            break


def _connect_pois_with_roads(
    bm: List[List[str]],
    pois: List[POI],
) -> List[List[bool]]:
    H = len(bm)
    W = len(bm[0]) if H else 0
    roads = [[False] * W for _ in range(H)]

    towns = [(p.x, p.y) for p in pois if p.type == "town"]
    castles = [(p.x, p.y) for p in pois if p.type == "castle"]

    def nearest(pt: Tuple[int, int], pool: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if not pool:
            return None
        return min(pool, key=lambda q: _manhattan(pt, q))

    for t in towns:
        target = nearest(t, castles) or nearest(t, [q for q in towns if q != t])
        if target:
            _lay_road(bm, roads, t, target)

    for i in range(len(castles) - 1):
        _lay_road(bm, roads, castles[i], castles[i + 1])

    return roads


# =============================================================================
# CACHE
# =============================================================================


def _cache_dir() -> str:
    return _data_path("cache")


def _cache_key(seed: int, W: int, H: int) -> str:
    return f"map_cache_seed{seed}_{W}x{H}.pkl"


def _cache_path(seed: int, W: int, H: int) -> str:
    _ensure_dir(_cache_dir())
    return os.path.join(_cache_dir(), _cache_key(seed, W, H))


# =============================================================================
# PUBLIC API
# =============================================================================


def generate_map() -> dict:
    """
    Core world generation entry point.

    Returns a dict with at least:
      {
        "width": int,
        "height": int,
        "seed": int,
        "heightmap": [[float]],
        "biomes": [[str]],
        "rivers": [[bool]],
        "roads": [[bool]],
        "locations": { "x,y": {...} }
      }
    """
    # ------------------------------------------------------------------
    # 1) Load config
    # ------------------------------------------------------------------
    cfg = _load_worldgen_cfg()
    W = int(cfg.get("width", _DEFAULT_WORLDGEN_CFG["width"]))
    H = int(cfg.get("height", _DEFAULT_WORLDGEN_CFG["height"]))
    seed = int(cfg.get("seed", _DEFAULT_WORLDGEN_CFG["seed"]))
    rng = random.Random(seed)

    # ------------------------------------------------------------------
    # 2) Try cache
    # ------------------------------------------------------------------
    cache_path = _cache_path(seed, W, H)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                cached = pickle.load(f)

            cached = _normalize_world_dict(cached)

            # Re-write normalized cache for future loads
            try:
                with open(cache_path, "wb") as wf:
                    pickle.dump(cached, wf)
            except Exception as e:
                logger.warning(f"Failed to rewrite normalized cache {cache_path}: {e}")

            logger.info(f"Loaded world map from cache: {cache_path}")
            return cached
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_path}: {e}; regenerating.")

    # ------------------------------------------------------------------
    # 3) Generate fresh world
    # ------------------------------------------------------------------
    # Heightmap
    hm = _heightmap(
        width=W,
        height=H,
        seed=seed,
        noise_cfg=cfg.get("noise", _DEFAULT_WORLDGEN_CFG["noise"]),
    )

    # Biome map
    biome_thresholds = _normalize_biome_thresholds(
        cfg.get("biomes", _DEFAULT_WORLDGEN_CFG["biomes"])
    )
    bm = _biomemap(hm, biome_thresholds)

    # Rivers
    river_count = int(cfg.get("rivers", _DEFAULT_WORLDGEN_CFG["rivers"]))
    rivers = _carve_rivers(hm, bm, river_count)

    # POIs
    poi_cfg = cfg.get("poi", _DEFAULT_WORLDGEN_CFG["poi"])
    pois = _place_pois(
        bm,
        counts={
            "towns": int(poi_cfg.get("towns", _DEFAULT_WORLDGEN_CFG["poi"]["towns"])),
            "castles": int(poi_cfg.get("castles", _DEFAULT_WORLDGEN_CFG["poi"]["castles"])),
            "dungeons": int(poi_cfg.get("dungeons", _DEFAULT_WORLDGEN_CFG["poi"]["dungeons"])),
        },
        min_spacing=int(poi_cfg.get("min_spacing", _DEFAULT_WORLDGEN_CFG["poi"]["min_spacing"])),
        rng=rng,
    )

    # Roads
    roads = _connect_pois_with_roads(bm, pois)

    # Locations dict
    locations: Dict[str, Dict] = {}
    town_i = castle_i = dungeon_i = 1
    for p in pois:
        if p.type == "town":
            name = f"Town {town_i}"
            town_i += 1
        elif p.type == "castle":
            name = f"Castle {castle_i}"
            castle_i += 1
        else:  # dungeon
            name = f"Dungeon {dungeon_i}"
            dungeon_i += 1

        locations[f"{p.x},{p.y}"] = {"type": p.type, "name": name}

    # ------------------------------------------------------------------
    # 4) Assemble final world
    # ------------------------------------------------------------------
    world = {
        "width": W,
        "height": H,
        "seed": seed,
        "heightmap": hm,
        "biomes": bm,
        "rivers": rivers,
        "roads": roads,
        "locations": locations,
    }

    # ------------------------------------------------------------------
    # 5) Cache it
    # ------------------------------------------------------------------
    try:
        with open(cache_path, "wb") as f:
            pickle.dump(world, f)
        logger.info(f"World map cached at {cache_path}")
    except Exception as e:
        logger.warning(f"Failed to write cache {cache_path}: {e}")

    return world


# =============================================================================
# CLI DEBUG (optional)
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate world map for debugging.")
    parser.add_argument("--dump-json", action="store_true", help="Write world.json into data/debug/")
    parser.add_argument("--dump-ascii", action="store_true", help="Write ascii_map.txt into data/debug/")
    args = parser.parse_args()

    world = generate_map()

    debug_dir = _data_path("debug")
    _ensure_dir(debug_dir)

    if args.dump_json:
        out = os.path.join(debug_dir, "world.json")
        _write_json(out, world)
        print(f"Wrote {out}")

    if args.dump_ascii:
        gfx = _read_json(
            _data_path("graphics.json"),
            {
                "tiles": {
                    "water": "~",
                    "sand": ".",
                    "grass": ",",
                    "forest": "T",
                    "mountain": "^",
                }
            },
        )
        tiles = gfx.get("tiles", {})
        bm = world["biomes"]
        roads = world["roads"]

        lines: List[str] = []
        for j in range(world["height"]):
            row = []
            for i in range(world["width"]):
                ch = tiles.get(bm[j][i], "?")
                if roads[j][i] and bm[j][i] != "water":
                    ch = "#"  # road over land
                row.append(ch)
            lines.append("".join(row))

        out = os.path.join(debug_dir, "ascii_map.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Wrote {out}")