"""
Core world generation orchestration.

This is the single implementation used by:
    dnd_adventure.map_generator.generate_map()
"""

from typing import Dict, List
import logging
import os

from .config import load_worldgen_cfg
from .biomes import generate_heightmap, generate_biome_map
from .rivers import carve_rivers
from .poi import place_pois, POI
from .roads import connect_pois_with_roads
from .cache import load_from_cache, save_to_cache
from .paths import data_path, ensure_dir

logger = logging.getLogger(__name__)

def generate_map() -> Dict:
    """
    Generate or load from cache a full world map structure.

    Returns dict with:
      width, height, seed,
      height: 2D float,
      biomes: 2D str,
      rivers: 2D bool,
      roads:  2D bool,
      locations: { "x,y": {"type": "...", "name": "..."} }
    """
    cfg = load_worldgen_cfg()
    W = int(cfg.get("width", 64))
    H = int(cfg.get("height", 48))
    seed = int(cfg.get("seed", 1337))

    cached = load_from_cache(seed, W, H)
    if cached:
        return cached

    # 1) Terrain & biomes
    hm = generate_heightmap(W, H, seed, cfg.get("noise", {}))
    bm = generate_biome_map(hm, cfg.get("biomes", {}))

    # 2) Rivers
    rivers = carve_rivers(hm, bm, int(cfg.get("rivers", 5)))

    # 3) POIs
    poi_cfg = cfg.get("poi", {})
    pois: List[POI] = place_pois(
        bm,
        {
            "towns": int(poi_cfg.get("towns", 6)),
            "castles": int(poi_cfg.get("castles", 3)),
            "dungeons": int(poi_cfg.get("dungeons", 6)),
        },
        min_spacing=int(poi_cfg.get("min_spacing", 4)),
        rng=__import__("random").Random(seed),
    )

    # 4) Roads
    roads = connect_pois_with_roads(bm, pois)

    # 5) Locations
    locations: Dict[str, Dict] = {}
    town_i = castle_i = dungeon_i = 1
    for p in pois:
        if p.type == "town":
            name = f"Town {town_i}"; town_i += 1
        elif p.type == "castle":
            name = f"Castle {castle_i}"; castle_i += 1
        else:
            name = f"Dungeon {dungeon_i}"; dungeon_i += 1
        locations[f"{p.x},{p.y}"] = {"type": p.type, "name": name}

    world = {
        "width": W,
        "height": H,
        "seed": seed,
        "height": hm,
        "biomes": bm,
        "rivers": rivers,
        "roads": roads,
        "locations": locations,
    }

    save_to_cache(seed, W, H, world)
    return world

# Optional: small CLI for debugging like original
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-json", action="store_true")
    parser.add_argument("--dump-ascii", action="store_true")
    args = parser.parse_args()

    world = generate_map()
    debug_dir = data_path("debug")
    ensure_dir(debug_dir)

    if args.dump_json:
        path = os.path.join(debug_dir, "world.json")
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(world, f, indent=2)
        print(f"Wrote {path}")

    if args.dump_ascii:
        import json
        gfx = {}
        try:
            with open(data_path("graphics.json"), "r", encoding="utf-8") as f:
                gfx = json.load(f)
        except FileNotFoundError:
            pass

        tiles = gfx.get("tiles", {
            "water": "~", "sand": "*", "grass": ".",
            "forest": "T", "mountain": "^"
        })
        bm = world["biomes"]
        roads = world["roads"]

        lines = []
        for j in range(world["height"]):
            row = []
            for i in range(world["width"]):
                ch = tiles.get(bm[j][i], "?")
                if roads[j][i] and bm[j][i] != "water":
                    ch = "#"
                row.append(ch)
            lines.append("".join(row))
        path = os.path.join(debug_dir, "ascii_map.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Wrote {path}")
