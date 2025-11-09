import logging
import json
import os
import random
import sys
from typing import Dict, Any, List

from dnd_adventure.room import Room, RoomType
from dnd_adventure.world import World
from dnd_adventure.npc import NPC
from dnd_adventure.worldgen.world_state import WorldState

# Ensure relative imports work when launched as a module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logger = logging.getLogger(__name__)


class GameWorld:
    def __init__(self, world: World, character_name: str, theme: str = "fantasy"):
        self.world = world
        self.rooms: Dict[str, Room] = {}
        self.character_name = character_name
        self.theme = theme
        self.starting_room_id: str | None = None

        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.saves_dir = os.path.join(self.project_root, "saves")
        self.world_dir = os.path.join(self.saves_dir, "worlds", f"{character_name}_world")

        self.theme_data = self.load_theme_data()
        self.world_state = self.load_or_generate_world()
        self.generate_rooms()

    def load_theme_data(self) -> Dict[str, Any]:
        data_dir = os.path.join(self.project_root, "data", "themes")
        theme_file = os.path.join(data_dir, f"{self.theme}.json")
        fallback_file = os.path.join(data_dir, "fantasy.json")

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded theme data: {theme_file}")
            return data
        except FileNotFoundError:
            logger.error(f"Theme file not found: {theme_file}; falling back to {fallback_file}")
            with open(fallback_file, "r", encoding="utf-8") as f:
                return json.load(f)

    def load_or_generate_world(self) -> WorldState:
        os.makedirs(self.world_dir, exist_ok=True)
        state_meta = os.path.join(self.world_dir, "state.meta")

        world_name = os.path.basename(self.world_dir)
        base_dir = self.project_root

        if os.path.exists(state_meta):
            logger.debug(f"Loading WorldState from {self.world_dir}")
            try:
                return self.load_world_state(self.world_dir, world_name, base_dir)
            except Exception as e:
                logger.error(f"Failed to load WorldState from {self.world_dir}: {e}")

        logger.debug(f"Generating new WorldState for {self.character_name}")
        ws = WorldState(world_name, base_dir)
        ws.generate()
        self.save_world_state(ws)
        return ws

    def load_world_state(self, world_dir: str, world_name: str, base_dir: str) -> WorldState:
        logger.debug(f"Loading WorldState from {world_dir}")
        ws = WorldState(world_name, base_dir)

        def _load_json_if_exists(path: str, default):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default

        ws.data = {
            "geography": _load_json_if_exists(os.path.join(world_dir, "geography.json"), {}),
            "biomes": _load_json_if_exists(os.path.join(world_dir, "biomes.json"), {}),
            "civilizations": _load_json_if_exists(os.path.join(world_dir, "civilizations.json"), []),
            "events": _load_json_if_exists(os.path.join(world_dir, "events.json"), []),
            "npcs": _load_json_if_exists(os.path.join(world_dir, "npcs.json"), []),
            "dialogues": _load_json_if_exists(os.path.join(world_dir, "dialogues.json"), []),
            "timeline": _load_json_if_exists(os.path.join(world_dir, "timeline.json"), []),
        }

        meta_path = os.path.join(world_dir, "state.meta")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                try:
                    meta = json.load(f)
                except Exception:
                    meta = {}
        else:
            meta = {}

        if "timeline" in meta and not ws.data.get("timeline"):
            ws.data["timeline"] = meta.get("timeline", [])
        if "dialogue" in meta and not ws.data.get("dialogues"):
            ws.data["dialogues"] = meta.get("dialogue", [])

        logger.info(f"Loaded WorldState for {world_name}")
        return ws

    def save_world_state(self, world_state: WorldState):
        logger.debug(f"Saving WorldState to {self.world_dir}")
        os.makedirs(self.world_dir, exist_ok=True)

        if hasattr(world_state, "data") and isinstance(world_state.data, dict):
            for key, value in world_state.data.items():
                path = os.path.join(self.world_dir, f"{key}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=2)
        else:
            attrs = ["geography", "biomes", "civilizations", "events", "npcs", "dialogues", "timeline"]
            for attr in attrs:
                if hasattr(world_state, attr):
                    path = os.path.join(self.world_dir, f"{attr}.json")
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(getattr(world_state, attr), f, indent=2)

        meta = {
            "world_name": getattr(world_state, "world_name", os.path.basename(self.world_dir)),
            "dialogue_count": len(world_state.data.get("dialogues", [])) if hasattr(world_state, "data") else 0,
            "event_count": len(world_state.data.get("events", [])) if hasattr(world_state, "data") else 0,
        }
        with open(os.path.join(self.world_dir, "state.meta"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        logger.info(f"Saved WorldState to {self.world_dir}")

    def generate_rooms(self) -> None:
        self.rooms = {}

        for i in range(5):
            for j in range(5):
                room_key = f"{i},{j}"
                room_type = RoomType("dungeon") if (i + j) % 2 == 0 else RoomType("plains")
                room_id = int(f"{i}{j}")
                name = f"Room {room_key}"
                description = f"A {'dark' if room_type.name == 'dungeon' else 'peaceful'} area at {room_key}"
                exits = {}

                room = Room(
                    room_id=room_id,
                    name=name,
                    description=description,
                    room_type=room_type,
                    exits=exits
                )
                self.rooms[room_key] = room

        preferred_start = next((rid for rid, r in self.rooms.items()
                                if r.room_type.name == "dungeon"), None)
        fallback = next(iter(self.rooms.keys()), None)
        self.starting_room_id = preferred_start or fallback

        if self.starting_room_id:
            logger.info(f"Starting room set to: {self.starting_room_id}")
        else:
            logger.error("No rooms generated — cannot set starting room.")

    def _create_templated_npcs(self, npc_templates: List[Dict[str, Any]], civ: Dict[str, Any] | None) -> List[NPC]:
        npcs: List[NPC] = []
        if not npc_templates:
            return npcs

        civ_name = civ["name"] if civ else "Wandering"
        civ_race = civ["race"] if civ else "unknown"

        for tpl in npc_templates:
            name = tpl["name"].replace("{civ_name}", civ_name)
            dialogue_lines = [d.replace("{civ_name}", civ_name) for d in tpl.get("dialogue", [])] or ["..."]
            npcs.append(
                NPC(
                    name=name,
                    race=civ_race,
                    profession=tpl.get("profession", "unknown"),
                    traits=tpl.get("traits", []),
                    dialogue=random.choice(dialogue_lines),
                )
            )
        return npcs

    def _ws_set(self, key: str, value: Any):
        if not hasattr(self.world_state, "data") or not isinstance(self.world_state.data, dict):
            self.world_state.data = {}
        self.world_state.data[key] = value

    def get_room(self, room_id: str) -> Room:
        return self.rooms.get(room_id)
