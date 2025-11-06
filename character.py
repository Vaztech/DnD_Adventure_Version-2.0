from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

@dataclass
class Character:
    name: str
    race: str
    subrace_name: Optional[str]
    class_name: str
    stats: Dict[str, int]
    known_spells: Dict[int, List[str]]
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10
    mp: int = 10
    max_mp: int = 10
    armor_class: int = 10
    bab: int = 0
    xp: int = 0
    domain: Optional[str] = None

    def __init__(
        self,
        name: str,
        race: str,
        subrace_name: Optional[str],
        class_name: str,
        stats: Dict[str, int],
        known_spells: Dict[int, List[str]],
        level: int = 1,
        hit_points: int = 10,
        max_hit_points: int = 10,
        mp: int = 10,
        max_mp: int = 10,
        armor_class: int = 10,
        bab: int = 0,
        xp: int = 0,
        domain: Optional[str] = None
    ):
        self.name = name
        self.race = race
        self.subrace_name = subrace_name
        self.class_name = class_name
        self.stats = stats
        self.known_spells = known_spells
        self.level = level
        self.hit_points = hit_points
        self.max_hit_points = max_hit_points
        self.mp = mp
        self.max_mp = max_mp
        self.armor_class = armor_class
        self.bab = bab
        self.xp = xp
        self.domain = domain
        logger.debug(f"Character created: {name}, {race}, {subrace_name}, {class_name}")

    def get_stat_modifier(self, stat_index: int) -> int:
        stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        stat_value = self.stats[stat_names[stat_index]]
        return (stat_value - 10) // 2

    def gain_xp(self, xp: int):
        self.xp += xp
        logger.debug(f"{self.name} gained {xp} XP, total: {self.xp}")

    def cast_spell(self, spell_name: str, target: Optional[object] = None) -> str:
        for level, spells in self.known_spells.items():
            if spell_name in spells:
                mp_cost = level + 1
                if self.mp >= mp_cost:
                    self.mp -= mp_cost
                    damage = random.randint(1, 8) + level * 2
                    if target:
                        target.hit_points -= damage
                        return f"{self.name} casts {spell_name} on {target.name} for {damage} damage! MP: {self.mp}/{self.max_mp}"
                    return f"{self.name} casts {spell_name}! MP: {self.mp}/{self.max_mp}"
                return f"Not enough MP to cast {spell_name}!"
        return f"{spell_name} is not known!"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "race": self.race,
            "subrace_name": self.subrace_name,
            "class_name": self.class_name,
            "stats": self.stats,
            "known_spells": self.known_spells,
            "level": self.level,
            "hit_points": self.hit_points,
            "max_hit_points": self.max_hit_points,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "armor_class": self.armor_class,
            "bab": self.bab,
            "xp": self.xp,
            "domain": self.domain
        }