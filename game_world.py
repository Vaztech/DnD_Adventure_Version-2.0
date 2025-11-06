import logging
import json
import os
import random
import sys
from typing import Dict
from dnd_adventure.room import Room, RoomType
from dnd_adventure.world import World
from dnd_adventure.npc import NPC
from dnd_adventure.worldgen.world_state import WorldState

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)

class GameWorld:
    def __init__(self, world: World, character_name: str, theme: str = "fantasy"):
        self.world = world
        self.rooms: Dict[str, Room] = {}
        self.character_name = character_name
        self.theme = theme
        self.world_dir = f"C:\\Users\\Vaz\\Desktop\\dnd_adventure\\saves\\worlds\\{character_name}_world"
        self.theme_data = self.load_theme_data()
        self.world_state = self.load_or_generate_world()
        self.generate_rooms()

    def load_theme_data(self) -> Dict:
        theme_file = os.path.join(os.path.dirname(__file__), 'data', 'themes', f"{self.theme}.json")
        try:
            with open(theme_file, 'r') as f:
                data = json.load(f)
            logger.debug(f"Loaded theme data: {theme_file}")
            return data
        except FileNotFoundError:
            logger.error(f"Theme file not found: {theme_file}, defaulting to fantasy")
            with open(os.path.join(os.path.dirname(__file__), 'data', 'themes', 'fantasy.json'), 'r') as f:
                return json.load(f)

    def load_or_generate_world(self) -> WorldState:
        if os.path.exists(self.world_dir):
            logger.debug(f"Loading WorldState from {self.world_dir}")
            try:
                return self.load_world_state(self.world_dir)
            except Exception as e:
                logger.error(f"Failed to load WorldState from {self.world_dir}: {e}")
                ws = WorldState()
                self.save_world_state(ws)
                return ws
        else:
            logger.debug(f"Generating new WorldState for {self.character_name}")
            ws = WorldState()
            self.save_world_state(ws)
            return ws

    def load_world_state(self, world_dir: str) -> WorldState:
        logger.debug(f"Loading WorldState from {world_dir}")
        try:
            ws = WorldState()
            with open(os.path.join(world_dir, 'geography.json'), 'r') as f:
                ws.geography = json.load(f)
            with open(os.path.join(world_dir, 'biomes.json'), 'r') as f:
                ws.biomes = json.load(f)
            with open(os.path.join(world_dir, 'civilizations.json'), 'r') as f:
                ws.civilizations = json.load(f)
            with open(os.path.join(world_dir, 'npcs.json'), 'r') as f:
                ws.npcs = json.load(f)
            with open(os.path.join(world_dir, 'events.json'), 'r') as f:
                ws.events = json.load(f)
            ws.timeline = {}
            for event in ws.events:
                year = event['year']
                if year not in ws.timeline:
                    ws.timeline[year] = []
                ws.timeline[year].append(event['description'])
            ws.dialogue = []
            for npc in ws.npcs:
                if npc['notable']:
                    related_events = [e['description'] for e in ws.events if npc['civ'] in e['description']]
                    if related_events:
                        race_prefix = {
                            'Dwarf': f"{npc['name']} grumbles: ",
                            'Elf': f"{npc['name']} says gracefully: ",
                            'Orc': f"{npc['name']} growls: ",
                            'Human': f"{npc['name']} says: "
                        }.get(npc['race'], f"{npc['name']} says: ")
                        ws.dialogue.append(f"{race_prefix}'{random.choice(related_events)}'")
            ws.civ_changes = []
            for civ in ws.civilizations:
                change = {
                    'name': civ['name'],
                    'race': civ['race'],
                    'subrace': civ.get('subrace'),
                    'power_change': 0,
                    'population_change': 0
                }
                ws.civ_changes.append(change)
            logger.info(f"Loaded WorldState from {world_dir}")
            return ws
        except Exception as e:
            logger.error(f"Failed to load WorldState from {world_dir}: {e}")
            return WorldState()

    def save_world_state(self, world_state: WorldState):
        logger.debug(f"Saving WorldState to {self.world_dir}")
        os.makedirs(self.world_dir, exist_ok=True)
        attrs = ["biomes", "civilizations", "events", "geography", "npcs"]
        for attr in attrs:
            with open(os.path.join(self.world_dir, f"{attr}.json"), "w") as f:
                json.dump(getattr(world_state, attr), f, indent=2)
        meta = {
            "civ_changes": world_state.civ_changes,
            "timeline": world_state.timeline,
            "dialogue": world_state.dialogue
        }
        with open(os.path.join(self.world_dir, "state.meta"), "w") as f:
            json.dump(meta, f, indent=2)
        logger.info(f"Saved WorldState to {self.world_dir}")

    def generate_rooms(self):
        logger.debug(f"Generating world rooms for theme {self.theme}")
        civ_templates = self.theme_data.get("civilizations", [])
        room_templates = self.theme_data.get("rooms", [])
        npc_templates = self.theme_data.get("npcs", [])
        events = self.theme_data.get("events", [])

        # Generate civilizations
        num_civs = min(len(civ_templates), 4)
        civilizations = []
        used_coords = set()
        for i in range(num_civs):
            template = random.choice(civ_templates)
            for _ in range(10):  # Retry up to 10 times for unique coords
                x, y = random.randint(0, 49), random.randint(0, 49)
                if (x, y) not in used_coords:
                    used_coords.add((x, y))
                    civ = {
                        "name": f"{template['name']}_{i}",
                        "race": template["race"],
                        "description": template["description"],
                        "capital": {"x": x, "y": y}
                    }
                    civilizations.append(civ)
                    break
        self.world_state.civilizations = civilizations

        # Generate capital rooms
        self.rooms = {}
        for civ in civilizations:
            x, y = civ['capital']['x'], civ['capital']['y']
            room_id = f"{x},{y}"
            capital_template = next((r for r in room_templates if r["type"] == "capital"), None)
            if not capital_template:
                logger.warning("No capital room template found, skipping")
                continue
            
            biome = random.choice(capital_template["biome"])
            name = capital_template["name"].replace("{civ_name}", civ["name"])
            description = capital_template["description"].replace("{civ_name}", civ["name"]).replace("{biome}", biome)
            room_type = RoomType.CASTLE if biome in ['plains', 'forest', 'grassland'] else RoomType.DUNGEON
            
            exits = {}
            for other_civ in civilizations:
                if other_civ != civ:
                    ox, oy = other_civ['capital']['x'], other_civ['capital']['y']
                    if abs(x - ox) + abs(y - oy) <= 10:
                        exits[random.choice(['north', 'south', 'east', 'west'])] = f"{ox},{oy}"
            
            npcs = []
            for npc_name in capital_template.get("npcs", []):
                npc_template = next((n for n in npc_templates if n["name"] == npc_name), None)
                if npc_template:
                    npc_name = npc_template["name"].replace("{civ_name}", civ["name"])
                    dialogue = [d.replace("{civ_name}", civ["name"]) for d in npc_template["dialogue"]]
                    npcs.append(NPC(
                        name=npc_name,
                        race=civ["race"],
                        profession="unknown",
                        traits=[],
                        dialogue=random.choice(dialogue)
                    ))
            
            self.rooms[room_id] = Room(
                room_id=int(room_id.replace(",", "")),
                name=name,
                description=description,
                room_type=room_type,
                exits=exits,
                npcs=npcs
            )
            logger.debug(f"Room initialized: {name} at ({x},{y}) (ID: {room_id}, Type: {room_type.value})")
        
        # Generate extra rooms
        target_rooms = random.randint(6, 10)
        non_capital_templates = [r for r in room_templates if r["type"] != "capital"]
        attempts = 0
        while len(self.rooms) < target_rooms and non_capital_templates and attempts < 50:
            template = random.choice(non_capital_templates)
            x, y = random.randint(0, 49), random.randint(0, 49)
            room_id = f"{x},{y}"
            if room_id in self.rooms or (x, y) in used_coords:
                attempts += 1
                continue
            used_coords.add((x, y))
            
            biome = random.choice(template["biome"])
            name = template["name"]
            description = template["description"].replace("{biome}", biome)
            room_type = RoomType.DUNGEON
            
            exits = {random.choice(['north', 'south', 'east', 'west']): random.choice(list(self.rooms.keys()))}
            
            npcs = []
            for npc_name in template.get("npcs", []):
                npc_template = next((n for n in npc_templates if n["name"] == npc_name), None)
                if npc_template:
                    dialogue = [d.replace("{civ_name}", random.choice(civilizations)["name"]) for d in npc_template["dialogue"]]
                    npcs.append(NPC(
                        name=npc_template["name"],
                        race="unknown",
                        profession="unknown",
                        traits=[],
                        dialogue=random.choice(dialogue)
                    ))
            
            self.rooms[room_id] = Room(
                room_id=int(room_id.replace(",", "")),
                name=name,
                description=description,
                room_type=room_type,
                exits=exits,
                npcs=npcs,
                monsters=template.get("monsters", [])
            )
            logger.debug(f"Room initialized: {name} at ({x},{y}) (ID: {room_id}, Type: {room_type.value})")
            attempts = 0
        
        self.world_state.npcs = [
            {
                "name": npc.name,
                "race": npc.race,
                "civ": next((civ["name"] for civ in civilizations if npc.name.startswith(civ["name"])), "unknown"),
                "profession": npc.profession,
                "traits": npc.traits,
                "notable": True
            } for room in self.rooms.values() for npc in room.npcs
        ]
        self.world_state.events = events
        self.world_state.dialogue = [npc.dialogue for room in self.rooms.values() for npc in room.npcs]
        
        logger.info(f"Generated {len(self.rooms)} rooms")
        self.save_world_state(self.world_state)

    def get_room(self, room_id: str) -> Room:
        return self.rooms.get(room_id)