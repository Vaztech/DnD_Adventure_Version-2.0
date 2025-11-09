"""
River carving from high peaks toward water/edges.
"""

from typing import List, Tuple

def _neighbors(i: int, j: int, W: int, H: int):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        x, y = i + dx, j + dy
        if 0 <= x < W and 0 <= y < H:
            yield x, y

def _find_local_peaks(hm: List[List[float]], count: int) -> List[Tuple[int, int]]:
    H = len(hm)
    W = len(hm[0]) if H else 0
    cands = []
    for j in range(H):
        for i in range(W):
            h = hm[j][i]
            if all(h >= hm[y][x] for (x,y) in _neighbors(i,j,W,H)):
                cands.append((i,j,h))
    cands.sort(key=lambda t: t[2], reverse=True)
    return [(i,j) for (i,j,_) in cands[:count]]

def carve_rivers(hm, bm, river_count: int) -> List[List[bool]]:
    H = len(hm); W = len(hm[0]) if H else 0
    rivers = [[False]*W for _ in range(H)]
    sources = _find_local_peaks(hm, river_count)

    for (sx, sy) in sources:
        i, j = sx, sy
        visited = set()
        for _ in range(W*H*2):
            visited.add((i,j))
            rivers[j][i] = True
            if bm[j][i] == "water" or i == 0 or j == 0 or i == W-1 or j == H-1:
                break
            neigh = list(_neighbors(i,j,W,H))
            neigh.sort(key=lambda xy: hm[xy[1]][xy[0]])
            moved = False
            for (nx,ny) in neigh:
                if (nx,ny) in visited:
                    continue
                if hm[ny][nx] <= hm[j][i] + 0.01:
                    i, j = nx, ny
                    moved = True
                    break
            if not moved and neigh:
                i, j = neigh[0]

    for j in range(H):
        for i in range(W):
            if rivers[j][i]:
                bm[j][i] = "water"

    return rivers
