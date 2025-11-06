import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dnd_adventure.worldgen.geography_generator import generate_geography
from dnd_adventure.worldgen.biome_generator import assign_biomes
from dnd_adventure.worldgen.civilization_generator import generate_civilizations
from dnd_adventure.worldgen.event_simulator import simulate_events
from dnd_adventure.worldgen.npc_simulator import generate_npcs
from dnd_adventure.worldgen.timeline_manager import log_events
from dnd_adventure.worldgen.dialogue_generator import generate_dialogue

class WorldState:
    def __init__(self):
        self.geography = generate_geography()
        self.biomes = assign_biomes(self.geography)
        self.civilizations = generate_civilizations(self.biomes)
        initial_civs = [c.copy() for c in self.civilizations]
        self.npcs = generate_npcs(self.civilizations)
        self.events = simulate_events(self.civilizations)
        self.timeline = log_events(self.events)
        self.dialogue = generate_dialogue(self.npcs, self.events)
        
        self.civ_changes = []
        for initial, current in zip(initial_civs, self.civilizations):
            change = {
                "name": initial["name"],
                "race": initial["race"],
                "subrace": initial.get("subrace"),
                "power_change": current["power"] - initial["power"],
                "population_change": current["population"] - initial["population"]
            }
            self.civ_changes.append(change)

    def summary(self):
        print("\n=== World Summary ===")
        print("\nCivilizations:")
        for civ in self.civilizations:
            subrace_info = f" ({civ['subrace']})" if civ.get("subrace") else ""
            print(f" - {civ['name']} ({civ['race']}{subrace_info}, {civ['alignment']})")
            print(f"   Capital at ({civ['capital']['x']}, {civ['capital']['y']})")
            print(f"   Population: {civ['population']}, Power: {civ['power']}")
        
        print("\nCivilization Changes:")
        for change in self.civ_changes:
            subrace_info = f" ({change['subrace']})" if change.get("subrace") else ""
            print(f" - {change['name']} ({change['race']}{subrace_info}): " +
                  f"Power {'+' if change['power_change'] >=0 else ''}{change['power_change']}, " +
                  f"Population {'+' if change['population_change'] >=0 else ''}{change['population_change']}")
        
        print(f"\nGenerated {len(self.events)} events and {len(self.npcs)} NPCs.")
        print("\nNotable NPC Dialogue:")
        for line in self.dialogue:
            print(f" - {line}")