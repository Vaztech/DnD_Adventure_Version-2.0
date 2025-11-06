import random

def generate_dialogue(npcs, events):
    lines = []
    for npc in npcs:
        if npc["notable"]:
            related_events = [e["description"] for e in events if npc["civ"] in e["description"]]
            if related_events:
                race_prefix = {
                    "Dwarf": f"{npc['name']} grumbles: ",
                    "Elf": f"{npc['name']} says gracefully: ",
                    "Orc": f"{npc['name']} growls: ",
                    "Human": f"{npc['name']} says: "
                }.get(npc["race"], f"{npc['name']} says: ")
                
                lines.append(f"{race_prefix}'{random.choice(related_events)}'")
    return lines