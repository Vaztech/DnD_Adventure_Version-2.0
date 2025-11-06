from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Spell:
    name: str
    level: int
    school: str
    subschool: Optional[str]
    descriptor: Optional[List[str]]
    casting_time: str
    components: Dict[str, bool]
    spell_range: str
    area: Optional[str]
    target: Optional[str]
    duration: str
    saving_throw: Optional[str]
    spell_resistance: Optional[bool]
    description: str
    classes: Dict[str, int]
    mp_cost: int
    min_level: int
    stat_requirement: Dict[str, int]
    primary_stat: Optional[str] = None
    domain: Optional[str] = None
    
    def can_cast(self, caster_level: int, ability_score: int) -> bool:
        if not self.primary_stat or not self.stat_requirement:
            logger.warning(f"No primary_stat or stat_requirement for {self.name}, assuming minimum")
            return caster_level >= self.min_level
        return caster_level >= self.min_level and ability_score >= self.stat_requirement.get(self.primary_stat, 10)
    
    def __str__(self) -> str:
        return f"{self.name} (Level {self.level} {self.school}, {self.mp_cost} MP)"
    
    def get_full_description(self) -> str:
        descriptors = ", ".join(self.descriptor) if self.descriptor else "None"
        stat_req = ", ".join(f"{k}: {v}" for k, v in self.stat_requirement.items())
        return f"""
{self.name}
Level: {self.level}
School: {self.school}
Descriptor: {descriptors}
Casting Time: {self.casting_time}
Range: {self.spell_range}
Target: {self.target or 'N/A'}
Area: {self.area or 'N/A'}
Duration: {self.duration}
Saving Throw: {self.saving_throw or 'None'}
Spell Resistance: {'Yes' if self.spell_resistance else 'No'}
MP Cost: {self.mp_cost}
Minimum Level: {self.min_level}
Primary Stat: {self.primary_stat or 'None'}
Stat Requirement: {stat_req}
Description: {self.description}
"""

CORE_SPELLS = {
    "Magic Missile": Spell(
        name="Magic Missile",
        level=1,
        school="Evocation",
        subschool=None,
        descriptor=["Force"],
        casting_time="1 standard action",
        components={"verbal": True, "somatic": True, "material": False, "focus": False, "divine_focus": False},
        spell_range="Medium (100 ft. + 10 ft./level)",
        area=None,
        target="Up to five creatures, no two of which can be more than 15 ft. apart",
        duration="Instantaneous",
        saving_throw="None",
        spell_resistance=True,
        description="A missile of magical energy darts forth and strikes its target.",
        classes={"Wizard": 1, "Sorcerer": 1},
        mp_cost=2,
        min_level=1,
        stat_requirement={"Intelligence": 11},
        primary_stat="Intelligence"
    ),
    "Fireball": Spell(
        name="Fireball",
        level=3,
        school="Evocation",
        subschool=None,
        descriptor=["Fire"],
        casting_time="1 standard action",
        components={"verbal": True, "somatic": True, "material": True, "focus": False, "divine_focus": False},
        spell_range="Long (400 ft. + 40 ft./level)",
        area="20-ft.-radius spread",
        target=None,
        duration="Instantaneous",
        saving_throw="Reflex half",
        spell_resistance=True,
        description="A fireball spell generates a searing explosion of flame.",
        classes={"Wizard": 3, "Sorcerer": 3},
        mp_cost=6,
        min_level=5,
        stat_requirement={"Intelligence": 13},
        primary_stat="Intelligence"
    )
}

def get_spell_by_name(name: str) -> Optional[Spell]:
    return CORE_SPELLS.get(name)

def get_spells_by_level(level: int) -> List[Spell]:
    return [spell for spell in CORE_SPELLS.values() if spell.level == level]

def get_spells_by_school(school: str) -> List[Spell]:
    return [spell for spell in CORE_SPELLS.values() if school.lower() == spell.school.lower()]

def get_spells_for_class(class_name: str, max_level: Optional[int] = None) -> List[Spell]:
    spells = [
        spell for spell in CORE_SPELLS.values() 
        if class_name in spell.classes
    ]
    if max_level is not None:
        spells = [spell for spell in spells if spell.classes.get(class_name, 99) <= max_level]
    return spells