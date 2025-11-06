from typing import Dict, List, Tuple, Optional
from dnd_adventure.world import World
from dnd_adventure.character import Character

class QuestManager:
    def __init__(self, world: World):
        self.world = world
        self.quests = self._generate_quests()
        self.active_quests = []

    def _generate_quests(self) -> List[Dict]:
        quests = [
            {
                "id": 1,
                "name": "Explore the Ancient Dungeon",
                "description": "Venture into a dungeon to uncover its secrets.",
                "objective": {"type": "reach", "location_type": "dungeon"},
                "reward": {"xp": 100, "item": "Ancient Amulet"}
            },
            {
                "id": 2,
                "name": "Visit the Capital City",
                "description": "Travel to a bustling city to meet the king.",
                "objective": {"type": "reach", "location_type": "city"},
                "reward": {"xp": 80, "item": "Royal Crest"}
            },
            {
                "id": 3,
                "name": "Clear the Whispering Wood",
                "description": "Rid the forest of lurking dangers.",
                "objective": {"type": "reach", "location_type": "forest"},
                "reward": {"xp": 90, "item": "Elven Cloak"}
            },
            {
                "id": 4,
                "name": "Seek the Crystal Lake",
                "description": "Find the mystical lake and retrieve a crystal.",
                "objective": {"type": "reach", "location_type": "lake"},
                "reward": {"xp": 85, "item": "Crystal Shard"}
            }
        ]
        return quests

    def quest_list(self):
        print("\nAvailable Quests:")
        for quest in self.quests:
            status = "Active" if quest in self.active_quests else "Available"
            print(f"[{status}] {quest['id']}: {quest['name']} - {quest['description']}")

    def start_quest(self, quest_id: int):
        quest = next((q for q in self.quests if q["id"] == quest_id), None)
        if not quest:
            print(f"Quest {quest_id} not found!")
            return
        if quest in self.active_quests:
            print(f"Quest {quest['name']} is already active!")
            return
        self.active_quests.append(quest)
        print(f"Started quest: {quest['name']}")

    def complete_quest(self, quest_id: int, player: Character, player_pos: Tuple[int, int], current_room: Optional[str]):
        quest = next((q for q in self.active_quests if q["id"] == quest_id), None)
        if not quest:
            print(f"Quest {quest_id} is not active!")
            return
        objective = quest["objective"]
        if objective["type"] == "reach":
            tile = self.world.get_location(*player_pos)
            if tile["type"] == objective["location_type"]:
                self.active_quests.remove(quest)
                player.gain_xp(quest["reward"]["xp"])
                print(f"Quest completed: {quest['name']}! Gained {quest['reward']['xp']} XP and {quest['reward']['item']}.")
            else:
                print(f"Quest {quest['name']} not completed. You need to reach a {objective['location_type']}.")