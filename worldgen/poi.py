"""
Placement of towns, castles, and dungeons with spacing & biome rules.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

@dataclass
class POI:
    x: int
    y: int
    type: str  # 'town' | 'castle' | 'dungeon'

def _manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def place_pois(bm: List[List[str]],
               counts: Dict[str,int],
               min_spacing: int,
               rng: random.Random) -> List[POI]:
    H = len(bm); W = len(bm[0]) if H else 0
    pois: List[POI] = []

    def can_place(kind: str, x: int, y: int) -> bool:
        b = bm[y][x]
        if kind in ("town","castle"):
            if b not in ("grass","forest"):
                return False
        elif kind == "dungeon":
            if b not in ("mountain","forest","grass"):
                return False
        for p in pois:
            if _manhattan((p.x,p.y),(x,y)) < min_spacing:
                return False
        return True

    def spawn(kind: str, attempts: int):
        for _ in range(attempts):
            x = rng.randrange(W)
            y = rng.randrange(H)
            if can_place(kind, x, y):
                pois.append(POI(x,y,kind))
                return

    for _ in range(counts.get("castles",0)):
        spawn("castle", 4000)
    for _ in range(counts.get("towns",0)):
        spawn("town", 4000)
    for _ in range(counts.get("dungeons",0)):
        spawn("dungeon", 4000)

    return pois
