"""
Deterministic 2D value noise + FBM used for terrain heightmap.
"""

import math

def _hash2i(x: int, y: int, seed: int) -> int:
    n = (x * 0x1f1f1f1f) ^ (y * 0x5f356495) ^ seed
    n ^= (n >> 13)
    n *= 0x85ebca6b
    n ^= (n >> 16)
    return n & 0xFFFFFFFF

def _rand01(h: int) -> float:
    return (h % 1000003) / 1000003.0

def value_at(ix: int, iy: int, seed: int) -> float:
    return _rand01(_hash2i(ix, iy, seed))

def _smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)

def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def value_noise2d(x: float, y: float, seed: int) -> float:
    ix = int(math.floor(x))
    iy = int(math.floor(y))
    fx = x - ix
    fy = y - iy

    v00 = value_at(ix,     iy,     seed)
    v10 = value_at(ix + 1, iy,     seed)
    v01 = value_at(ix,     iy + 1, seed)
    v11 = value_at(ix + 1, iy + 1, seed)

    sx = _smoothstep(fx)
    sy = _smoothstep(fy)

    ix0 = _lerp(v00, v10, sx)
    ix1 = _lerp(v01, v11, sx)
    return _lerp(ix0, ix1, sy)

def fbm(x: float, y: float, seed: int,
        octaves: int, persistence: float, lacunarity: float) -> float:
    amp = 1.0
    freq = 1.0
    total = 0.0
    norm = 0.0
    for _ in range(octaves):
        total += value_noise2d(x * freq, y * freq, seed) * amp
        norm += amp
        amp *= persistence
        freq *= lacunarity
    return total / max(norm, 1e-9)
