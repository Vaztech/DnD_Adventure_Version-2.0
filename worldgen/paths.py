"""
Path helpers for worldgen.

Centralizes how we find the dnd_adventure root and data directory so
everything works on Windows/macOS/Linux regardless of cwd.
"""

import os

def pkg_root() -> str:
    # worldgen package is inside dnd_adventure/worldgen
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))

def data_path(*parts: str) -> str:
    return os.path.join(pkg_root(), "data", *parts)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
