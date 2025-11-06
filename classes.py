from typing import Dict, List, Optional
import random

class Character:
    def __init__(
        self,
        name: str,
        race_name: str,
        subrace_name: Optional[str],
        class_name: str,
        subclass_name: Optional[str],
        level: int,
        xp: int,
        stats: List[int],
        stat_dict: Dict[str, int],
        class_skills: List[str],
        features: List[Dict],
        class_data: Dict
    ):
        self.name = name
        self.race_name = race_name
        self.subrace_name = subrace_name
        self.class_name = class_name
        self.subclass_name = subclass_name
        self.level = level
        self.xp = xp
        self.stats = stats
        self.stat_dict = stat_dict
        self.class_skills = class_skills
        self.features = features
        self.class_data = class_data
        self.bab = self.calculate_bab()
        self.armor_class = self.calculate_ac()
        self.max_hit_points = self.calculate_hp()
        self.hit_points = self.max_hit_points
        self.max_mp = self.calculate_mp()
        self.mp = self.max_mp
        self.known_spells = {i: [] for i in range(10)}

    def calculate_bab(self) -> int:
        bab_progression = {
            "Wizard": [0, 0, 1, 1, 2, 2, 3, 3, 4, 4],
            "Sorcerer": [0, 0, 1, 1, 2, 2, 3, 3, 4, 4],
            "Cleric": [0, 1, 2, 3, 3, 4, 5, 6, 6, 7],
            "Druid": [0, 1, 2, 3, 3, 4, 5, 6, 6, 7],
            "Bard": [0, 1, 2, 3, 3, 4, 5, 6, 6, 7],
            "Paladin": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "Ranger": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }
        level = min(self.level, 10)
        return bab_progression.get(self.class_name, [0] * 10)[level - 1]

    def calculate_ac(self) -> int:
        dex_modifier = self.get_stat_modifier(1)
        return 10 + dex_modifier

    def calculate_hp(self) -> int:
        hit_die = {
            "Wizard": 6,
            "Sorcerer": 6,
            "Cleric": 8,
            "Druid": 8,
            "Bard": 8,
            "Paladin": 10,
            "Ranger": 10
        }.get(self.class_name, 6)
        con_modifier = self.get_stat_modifier(2)
        return hit_die + con_modifier * self.level

    def calculate_mp(self) -> int:
        preferred_stat = {
            "Wizard": "Intelligence",
            "Sorcerer": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Bard": "Charisma",
            "Paladin": "Wisdom",
            "Ranger": "Wisdom"
        }.get(self.class_name, "Intelligence")
        stat_modifier = (self.stat_dict.get(preferred_stat, 10) - 10) // 2
        return 10 + self.level * stat_modifier

    def get_stat_modifier(self, stat_index: int) -> int:
        return (self.stats[stat_index] - 10) // 2

    def cast_spell(self, spell_name: str, target: Optional[object]) -> str:
        from dnd_adventure.spells import get_spell_by_name
        spell = get_spell_by_name(spell_name)
        if not spell:
            return f"Spell {spell_name} not found!"
        if spell_name not in sum(self.known_spells.values(), []):
            return f"{self.name} does not know {spell_name}!"
        mp_cost = spell.mp_cost
        if self.mp < mp_cost:
            return f"Not enough MP to cast {spell_name}! (Need {mp_cost}, have {self.mp})"
        primary_stat = spell.primary_stat or self.get_preferred_stat()
        ability_score = self.stat_dict.get(primary_stat, 10)
        if not spell.can_cast(self.level, ability_score):
            return f"Cannot cast {spell_name}: level or stat requirements not met!"
        
        self.mp -= mp_cost
        damage = 0
        if spell.name == "Magic Missile":
            num_missiles = max(1, self.level // 2)
            modifier = self.get_stat_modifier(self.get_preferred_stat_index())
            damage = sum(random.randint(1, 4) + 1 + modifier for _ in range(num_missiles))
        elif spell.name == "Fireball":
            modifier = self.get_stat_modifier(self.get_preferred_stat_index())
            damage = sum(random.randint(1, 6) for _ in range(min(10, self.level))) + modifier
        elif spell.name == "Storm of Vengeance":
            modifier = self.get_stat_modifier(self.get_preferred_stat_index())
            damage = sum(random.randint(1, 6) for _ in range(10)) + modifier  # Simplified: 10d6 acid/lightning damage
        
        if target and damage > 0:
            target.hit_points = max(0, target.hit_points - damage)
            return f"{self.name} casts {spell_name} on {target.name} for {damage} damage! MP: {self.mp}/{self.max_mp}"
        return f"{self.name} casts {spell_name}! MP: {self.mp}/{self.max_mp}"

    def get_preferred_stat(self) -> str:
        return {
            "Wizard": "Intelligence",
            "Sorcerer": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Bard": "Charisma",
            "Paladin": "Wisdom",
            "Ranger": "Wisdom"
        }.get(self.class_name, "Intelligence")

    def get_preferred_stat_index(self) -> int:
        stat_map = {
            "Strength": 0,
            "Dexterity": 1,
            "Constitution": 2,
            "Intelligence": 3,
            "Wisdom": 4,
            "Charisma": 5
        }
        return stat_map.get(self.get_preferred_stat(), 3)

    def gain_xp(self, xp: int):
        self.xp += xp
        print(f"{self.name} gained {xp} XP! Total XP: {self.xp}")

    def check_subclass_eligibility(self, classes: Dict, subclass_name: str) -> bool:
        dnd_class = classes.get(self.class_name, {})
        subclass = dnd_class.get("subclasses", {}).get(subclass_name)
        if not subclass:
            return False
        prereqs = subclass.get("prerequisites", {})
        if self.level < prereqs.get("level", 1):
            return False
        for stat, req in prereqs.get("stats", {}).items():
            if self.stat_dict.get(stat, 0) < req:
                return False
        return True

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "race_name": self.race_name,
            "subrace_name": self.subrace_name,
            "class_name": self.class_name,
            "subclass_name": self.subclass_name,
            "level": self.level,
            "xp": self.xp,
            "stats": self.stats,
            "stat_dict": self.stat_dict,
            "max_hit_points": self.max_hit_points,
            "hit_points": self.hit_points,
            "max_mp": self.max_mp,
            "mp": self.mp,
            "known_spells": self.known_spells,
            "class_skills": self.class_skills,
            "features": self.features,
            "class_data": self.class_data,
            "bab": self.bab,
            "armor_class": self.armor_class
        }