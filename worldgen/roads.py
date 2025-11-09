"""
Simple greedy road generation between POIs.
"""

from typing import List, Tuple, Optional
from .poi import POI

def _neighbors(i: int, j: int, W: int, H: int):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        x, y = i + dx, j + dy
        if 0 <= x < W and 0 <= y < H:
            yield x, y

def _manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _pass_cost(biome: str) -> int:
    return {
        "water": 9999,
        "sand": 6,
        "grass": 3,
        "forest": 5,
        "mountain": 8,
    }.get(biome, 4)

def _lay_road(bm, roads, start: Tuple[int,int], end: Tuple[int,int]):
    H = len(bm); W = len(bm[0]) if H else 0
    x, y = start
    tx, ty = end
    steps = 0
    max_steps = W * H
    while (x,y) != (tx,ty) and steps < max_steps:
        steps += 1
        candidates = list(_neighbors(x,y,W,H))
        candidates.sort(key=lambda xy: (
            _pass_cost(bm[xy[1]][xy[0]]),
            _manhattan(xy, (tx,ty))
        ))
        moved = False
        for nx,ny in candidates:
            if bm[ny][nx] == "water":
                continue
            x, y = nx, ny
            roads[ny][nx] = True
            moved = True
            break
        if not moved:
            break

def _nearest(pt: Tuple[int,int], pool: List[Tuple[int,int]]) -> Optional[Tuple[int,int]]:
    if not pool:
        return None
    return min(pool, key=lambda q: _manhattan(pt,q))

def connect_pois_with_roads(bm: List[List[str]], pois: List[POI]) -> List[List[bool]]:
    H = len(bm); W = len(bm[0]) if H else 0
    roads = [[False]*W for _ in range(H)]

    towns = [(p.x,p.y) for p in pois if p.type == "town"]
    castles = [(p.x,p.y) for p in pois if p.type == "castle"]

    for t in towns:
        target = _nearest(t, castles) or _nearest(t, [q for q in towns if q != t])
        if target:
            _lay_road(bm, roads, t, target)

    for i in range(len(castles)-1):
        _lay_road(bm, roads, castles[i], castles[i+1])

    return roads
