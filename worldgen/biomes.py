"""
Heightmap + biome assignment utilities.
"""

from typing import List
from .noise import fbm

def generate_heightmap(width: int, height: int, seed: int, noise_cfg: dict) -> List[List[float]]:
    scale = max(1e-6, float(noise_cfg.get("scale", 32.0)))
    octaves = int(noise_cfg.get("octaves", 4))
    persistence = float(noise_cfg.get("persistence", 0.5))
    lacunarity = float(noise_cfg.get("lacunarity", 2.0))

    hm = [[0.0] * width for _ in range(height)]

    for j in range(height):
        for i in range(width):
            x = (i + 1000) / scale
            y = (j + 1000) / scale
            hm[j][i] = fbm(x, y, seed, octaves, persistence, lacunarity)

    lo = min(min(row) for row in hm)
    hi = max(max(row) for row in hm)
    rng = max(hi - lo, 1e-9)
    for j in range(height):
        for i in range(width):
            hm[j][i] = (hm[j][i] - lo) / rng

    return hm

def _biome_from_height(h: float, th: dict) -> str:
    if h < th["water"]:
        return "water"
    if h < th["sand"]:
        return "sand"
    if h < th["grass"]:
        return "grass"
    if h < th["forest"]:
        return "forest"
    return "mountain"

def generate_biome_map(hm: List[List[float]], thresholds: dict) -> List[List[str]]:
    H = len(hm)
    W = len(hm[0]) if H else 0
    bm = [["grass"] * W for _ in range(H)]
    for j in range(H):
        for i in range(W):
            bm[j][i] = _biome_from_height(hm[j][i], thresholds)
    return bm
