from typing import List, Dict, Optional

class RacialTrait:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class Race:
    def __init__(
        self,
        name: str,
        description: str,
        ability_modifiers: Dict[str, int],
        size: str,
        speed: int,
        racial_traits: List[Dict[str, str]],
        favored_class: str,
        languages: List[str],
        subraces: Dict[str, Dict] = None
    ):
        self.name = name
        self.description = description
        self.ability_modifiers = ability_modifiers
        self.size = size
        self.speed = speed
        self.racial_traits = [RacialTrait(t['name'], t['description']) for t in racial_traits]
        self.favored_class = favored_class
        self.languages = languages
        self.subraces = subraces or {}
        self.subrace = None

    def apply_modifiers(self, character: 'Character') -> None:
        """
        Apply racial and subrace ability modifiers to the character's stats.
        Stats are ordered: [Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma]
        """
        stat_indices = {
            'Strength': 0,
            'Dexterity': 1,
            'Constitution': 2,
            'Intelligence': 3,
            'Wisdom': 4,
            'Charisma': 5
        }
        # Apply base race modifiers
        for stat, modifier in self.ability_modifiers.items():
            if stat in stat_indices:
                character.stats[stat_indices[stat]] += modifier
        # Apply subrace modifiers if selected
        if self.subrace and self.subraces and self.subrace in self.subraces:
            subrace_modifiers = self.subraces[self.subrace].get('ability_modifiers', {})
            for stat, modifier in subrace_modifiers.items():
                if stat in stat_indices:
                    character.stats[stat_indices[stat]] += modifier