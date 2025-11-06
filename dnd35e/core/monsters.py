import json
from pathlib import Path
from typing import List, Dict, Optional

class Attack:
    def __init__(self, name: str, damage: str, attack_bonus: int = 0, special: Optional[str] = None):
        self.name = name
        self.damage = damage
        self.attack_bonus = attack_bonus
        self.special = special

    def __repr__(self):
        return f"Attack({self.name}, DMG: {self.damage}, Bonus: {self.attack_bonus}, Special: {self.special})"

class Monster:
    def __init__(self,
                 name: str,
                 type: str,
                 armor_class: int,
                 hit_points: int,
                 speed: int,
                 challenge_rating: float,
                 abilities: Optional[Dict[str, int]] = None,
                 attacks: Optional[List[Attack]] = None,
                 spell_like_abilities: Optional[Dict[str, str]] = None,
                 abilities_list: Optional[List] = None):
        self.name = name
        self.type = type
        self.armor_class = armor_class
        self.hit_points = hit_points
        self.speed = speed
        self.challenge_rating = challenge_rating
        self.abilities = abilities or {
            "STR": 10,
            "DEX": 10,
            "CON": 10,
            "INT": 10,
            "WIS": 10,
            "CHA": 10
        }
        self.attacks = attacks or []
        self.spell_like_abilities = spell_like_abilities or {}
        self.abilities_list = abilities_list or []

    def __repr__(self):
        return (f"Monster({self.name}, Type: {self.type}, CR: {self.challenge_rating}, "
                f"AC: {self.armor_class}, HP: {self.hit_points}, SPD: {self.speed}, "
                f"Abilities: {self.abilities}, Attacks: {self.attacks})")

class MonsterTemplate:
    def __init__(self, name: str, cr: float, monster_type: str, armor_class: int, hit_points: int, speed: int):
        self.name = name
        self.cr = cr
        self.type = monster_type
        self.armor_class = armor_class
        self.hit_points = hit_points
        self.speed = speed

    def __repr__(self):
        return f"MonsterTemplate({self.name}, CR: {self.cr}, Type: {self.type}, AC: {self.armor_class}, HP: {self.hit_points}, Speed: {self.speed})"

def load_monsters_from_json() -> List[Monster]:
    """Load monsters from a JSON file and convert to Monster objects."""
    try:
        base_path = Path(__file__).resolve().parent.parent.parent
        json_path = base_path / 'data' / 'srd_monsters.json'

        if not json_path.exists():
            print(f"Error: The file {json_path} does not exist.")
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        monsters = []

        for category, category_data in data.items():
            for name, monster_data in category_data.items():
                try:
                    monster_type = monster_data.get('type', 'Unknown')
                    armor_class = monster_data.get('armor_class', 10)
                    hit_points = monster_data.get('hit_points', 1)
                    speed = monster_data.get('speed', 30)
                    cr = monster_data.get('challenge_rating', 0.25)

                    abilities = monster_data.get('abilities', {
                        "STR": 10, "DEX": 10, "CON": 10,
                        "INT": 10, "WIS": 10, "CHA": 10
                    })

                    attacks_data = monster_data.get('attacks', [])
                    attacks = []
                    for atk in attacks_data:
                        attacks.append(
                            Attack(
                                name=atk.get('name', 'Claw'),
                                damage=atk.get('damage', '1d4'),
                                attack_bonus=atk.get('attack_bonus', 0),
                                special=atk.get('special')
                            )
                        )

                    monster = Monster(
                        name=name,
                        type=monster_type,
                        armor_class=armor_class,
                        hit_points=hit_points,
                        speed=speed,
                        challenge_rating=cr,
                        abilities=abilities,
                        attacks=attacks,
                        spell_like_abilities=monster_data.get('spell_like_abilities'),
                        abilities_list=monster_data.get('abilities_list')
                    )

                    monsters.append(monster)
                except Exception as e:
                    print(f"Warning: Failed to parse monster '{name}': {e}")

        return monsters

    except Exception as e:
        print(f"Error processing monster JSON: {e}")
        return []

SRD_MONSTERS = load_monsters_from_json()

def get_monsters_by_cr(cr: float) -> List[Monster]:
    return [m for m in SRD_MONSTERS if m.challenge_rating == cr]

def get_monsters_by_type(monster_type: str) -> List[Monster]:
    return [m for m in SRD_MONSTERS if m.type.lower() == monster_type.lower()]

def get_monster_by_name(name: str) -> Optional[Monster]:
    for m in SRD_MONSTERS:
        if m.name.lower() == name.lower():
            return m
    return None

def get_monster_by_cr(cr: float) -> Optional[Monster]:
    for m in SRD_MONSTERS:
        if m.challenge_rating == cr:
            return m
    return None

def get_monster_by_ac(ac: int) -> Optional[Monster]:
    for m in SRD_MONSTERS:
        if m.armor_class == ac:
            return m
    return None