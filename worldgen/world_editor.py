import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dnd_adventure.worldgen.world_state import WorldState

def print_menu():
    print("\n=== World Editor Menu ===")
    print("1. View Civilizations")
    print("2. View NPCs")
    print("3. View Timeline Events by Year")
    print("4. View Notable Dialogue")
    print("5. Exit")

def view_civilizations(world):
    for civ in world.civilizations:
        print(f"- {civ['name']} ({civ['race']}) at ({civ['capital']['x']}, {civ['capital']['y']})")
        print(f"  Alignment: {civ['alignment']}, Culture: {civ['culture']}, Pop: {civ['population']}, Power: {civ['power']}\n")

def view_npcs(world):
    for npc in world.npcs:
        print(f"- {npc['name']} ({npc['race']}) of {npc['civ']}")
        print(f"  Profession: {npc['profession']}, Notable: {npc['notable']}, Traits: {', '.join(npc['traits'])}\n")

def view_timeline(world):
    try:
        year = int(input("Enter year to view events: "))
        events = world.timeline.get(year, [])
        if events:
            print(f"\nEvents in Year {year}:")
            for e in events:
                print(f" - {e}")
        else:
            print(f"No recorded events for year {year}.")
    except ValueError:
        print("Invalid input. Please enter a numeric year.")

def view_dialogue(world):
    for line in world.dialogue:
        print(f" - {line}")

if __name__ == "__main__":
    world = WorldState()
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()
        if choice == "1":
            view_civilizations(world)
        elif choice == "2":
            view_npcs(world)
        elif choice == "3":
            view_timeline(world)
        elif choice == "4":
            view_dialogue(world)
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please try again.")