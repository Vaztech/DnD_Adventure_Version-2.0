from enum import Enum
from typing import Dict, List, Optional, Callable
import logging
from dnd_adventure.dnd35e.core.monsters import Monster
from dnd_adventure.dnd35e.core import Item, Trap, Puzzle, LightSource
from dnd_adventure.npc import NPC

logger = logging.getLogger(__name__)

class RoomType(Enum):
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    CASTLE = "castle"
    TEMPLE = "temple"
    CAVE = "cave"

class Room:
    def __init__(
        self,
        room_id: int,
        name: str,
        description: str,
        room_type: RoomType,
        exits: Dict[str, str],
        monsters: Optional[List[Monster]] = None,
        items: Optional[List[Item]] = None,
        traps: Optional[List[Trap]] = None,
        puzzles: Optional[List[Puzzle]] = None,
        light_sources: Optional[List[LightSource]] = None,
        npcs: Optional[List[NPC]] = None,
        on_enter: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        visited: bool = False
    ):
        self.room_id = room_id
        self.name = name
        self.description = description
        self.room_type = room_type
        self.exits = exits
        self.monsters = monsters if monsters is not None else []
        self.items = items if items is not None else []
        self.traps = traps if traps is not None else []
        self.puzzles = puzzles if puzzles is not None else []
        self.light_sources = light_sources if light_sources is not None else []
        self.npcs = npcs if npcs is not None else []
        self.on_enter = on_enter
        self.on_exit = on_exit
        self.visited = visited
        self.is_lit = self._determine_initial_lighting()
        logger.debug(f"Room initialized: {self.name} (ID: {self.room_id}, Type: {self.room_type.value})")

    def _determine_initial_lighting(self) -> bool:
        if self.room_type in [RoomType.TOWN, RoomType.TEMPLE]:
            return True
        return any(light.is_active for light in self.light_sources)

    def add_monster(self, monster: Monster):
        self.monsters.append(monster)
        logger.debug(f"Added monster {monster.name} to room {self.name}")

    def add_item(self, item: Item):
        self.items.append(item)
        logger.debug(f"Added item {item.name} to room {self.name}")

    def add_trap(self, trap: Trap):
        self.traps.append(trap)
        logger.debug(f"Added trap {trap.name} to room {self.name}")

    def add_puzzle(self, puzzle: Puzzle):
        self.puzzles.append(puzzle)
        logger.debug(f"Added puzzle {puzzle.name} to room {self.name}")

    def add_light_source(self, light_source: LightSource):
        self.light_sources.append(light_source)
        self.update_lighting()
        logger.debug(f"Added light source {light_source.name} to room {self.name}")

    def add_npc(self, npc: NPC):
        self.npcs.append(npc)
        logger.debug(f"Added NPC {npc.name} to room {self.name}")

    def remove_monster(self, monster: Monster):
        if monster in self.monsters:
            self.monsters.remove(monster)
            logger.debug(f"Removed monster {monster.name} from room {self.name}")

    def remove_item(self, item: Item):
        if item in self.items:
            self.items.remove(item)
            logger.debug(f"Removed item {item.name} from room {self.name}")

    def trigger_traps(self, character):
        for trap in self.traps:
            if not trap.disarmed:
                trap.trigger(character)
                logger.debug(f"Triggered trap {trap.name} in room {self.name}")

    def attempt_puzzle(self, character, solution: str) -> bool:
        for puzzle in self.puzzles:
            if not puzzle.solved:
                solved = puzzle.attempt_solution(character, solution)
                if solved:
                    logger.debug(f"Solved puzzle {puzzle.name} in room {self.name}")
                    return True
        return False

    def update_lighting(self):
        previous_state = self.is_lit
        self.is_lit = any(light.is_active for light in self.light_sources) or self.room_type in [RoomType.TOWN, RoomType.TEMPLE]
        if self.is_lit != previous_state:
            logger.debug(f"Lighting changed in room {self.name}: is_lit={self.is_lit}")

    def extinguish_light(self, light_source: LightSource):
        if light_source in self.light_sources:
            light_source.is_active = False
            self.update_lighting()
            logger.debug(f"Extinguished light source {light_source.name} in room {self.name}")

    def enter(self, character):
        self.visited = True
        self.trigger_traps(character)
        if self.on_enter:
            self.on_enter(character)
        if not self.is_lit and not any(monster.has_darkvision for monster in self.monsters):
            logger.debug(f"Room {self.name} is dark, visibility limited")
        logger.info(f"Character entered room {self.name} (ID: {self.room_id})")

    def exit(self, character):
        if self.on_exit:
            self.on_exit(character)
        logger.info(f"Character exited room {self.name} (ID: {self.room_id})")