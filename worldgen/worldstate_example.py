import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dnd_adventure.worldgen.world_state import WorldState

if __name__ == "__main__":
    world = WorldState()
    world.summary()