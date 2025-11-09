# dnd_adventure/worldgen/dialogue_generator.py
import random
from typing import List, Dict, Any

def generate_dialogue(npcs: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Generate dialogue snippets for NPCs based on world events.
    Works safely even if NPCs are missing the 'notable' field.
    """
    dialogues = []
    event_topics = [e["type"] for e in events] if events else []

    for npc in npcs:
        # Safely check if NPC is notable; fallback to False
        is_notable = npc.get("notable", npc.get("is_notable", False))
        name = npc.get("name", "Unknown NPC")
        civ = npc.get("home_civilization", "Unknown Civilization")
        profession = npc.get("profession", "Commoner")
        race = npc.get("race", "Unknown Race")

        if is_notable:
            topic = random.choice(event_topics) if event_topics else "Rumor"
            line = f"I once witnessed the great {topic.lower()} that changed {civ} forever!"
        else:
            chatter = [
                f"The {race.lower()} folk of {civ} have been busy lately.",
                f"As a {profession.lower()}, I don't trust outsiders wandering these lands.",
                f"They say another storm is coming from the east.",
                f"Life in {civ} isn't easy, but we make do.",
                f"Rumors say heroes walk among us once again.",
            ]
            line = random.choice(chatter)

        dialogues.append({
            "speaker": name,
            "text": line
        })

    return dialogues

# Optional quick test
if __name__ == "__main__":
    demo_npcs = [
        {"name": "Durin_101", "race": "Dwarf", "home_civilization": "Dwarf Empire", "is_notable": True},
        {"name": "Elora_207", "race": "Elf", "home_civilization": "Elf Dominion"},
    ]
    demo_events = [{"type": "War", "civilization": "Dwarf Empire"}]
    for d in generate_dialogue(demo_npcs, demo_events):
        print(f"{d['speaker']}: {d['text']}")
