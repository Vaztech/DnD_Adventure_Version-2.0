import json
import logging
from pathlib import Path
from typing import Dict, Any
from dnd_adventure.data_loaders.data_utils import ensure_data_dir

logger = logging.getLogger(__name__)

class ClassLoader:
    def __init__(self):
        self.data_dir = ensure_data_dir()

    def ensure_classes_file_exists(self) -> None:
        classes_path = self.data_dir / "classes.json"
        if not classes_path.exists():
            default_classes = {
                "Barbarian": {
                    "name": "Barbarian",
                    "description": "A fierce warrior fueled by rage, excelling in melee combat with high durability and strength.",
                    "hit_die": 12,
                    "base_attack_bonus": "good",
                    "saving_throws": {"Fort": "good", "Ref": "poor", "Will": "poor"},
                    "skill_points": 4,
                    "class_skills": ["Climb", "Craft", "Handle Animal", "Intimidate", "Jump", "Listen", "Ride", "Survival", "Swim"],
                    "spellcasting": None,
                    "features": [
                        {"name": "Rage", "level": 1, "description": "Gain +4 Strength, +4 Constitution, +2 Will saves, -2 AC for limited rounds"},
                        {"name": "Fast Movement", "level": 1, "description": "+10 ft. to base speed"}
                    ]
                },
                "Bard": {
                    "name": "Bard",
                    "description": "A charismatic performer who weaves magic through music and excels in social interactions.",
                    "hit_die": 6,
                    "base_attack_bonus": "average",
                    "saving_throws": {"Fort": "poor", "Ref": "good", "Will": "good"},
                    "skill_points": 6,
                    "class_skills": ["Appraise", "Balance", "Bluff", "Climb", "Concentration", "Craft", "Decipher Script", "Diplomacy", "Disguise", "Escape Artist", "Gather Information", "Hide", "Jump", "Knowledge (all)", "Listen", "Move Silently", "Perform", "Profession", "Sense Motive", "Sleight of Hand", "Speak Language", "Spellcraft", "Swim", "Tumble", "Use Magic Device"],
                    "spellcasting": {
                        "type": "arcane",
                        "ability": "Charisma",
                        "spells_known": "spontaneous"
                    },
                    "features": [
                        {"name": "Bardic Music", "level": 1, "description": "Inspire courage, fascinate, and other effects"},
                        {"name": "Bardic Knowledge", "level": 1, "description": "Bonus to Knowledge checks"}
                    ]
                },
                "Cleric": {
                    "name": "Cleric",
                    "description": "A divine spellcaster who channels the power of their deity to heal and protect allies.",
                    "hit_die": 8,
                    "base_attack_bonus": "average",
                    "saving_throws": {"Fort": "good", "Ref": "poor", "Will": "good"},
                    "skill_points": 2,
                    "class_skills": ["Concentration", "Craft", "Diplomacy", "Heal", "Knowledge (arcana)", "Knowledge (history)", "Knowledge (religion)", "Knowledge (the planes)", "Profession", "Spellcraft"],
                    "spellcasting": {
                        "type": "divine",
                        "ability": "Wisdom",
                        "spells_known": "prepared"
                    },
                    "features": [
                        {"name": "Turn Undead", "level": 1, "description": "Channel divine energy to turn undead"},
                        {"name": "Domains", "level": 1, "description": "Choose two domains for bonus spells and powers"}
                    ]
                },
                "Druid": {
                    "name": "Druid",
                    "description": "A nature-bound spellcaster who draws power from the wilderness and bonds with animals.",
                    "hit_die": 8,
                    "base_attack_bonus": "average",
                    "saving_throws": {"Fort": "good", "Ref": "poor", "Will": "good"},
                    "skill_points": 4,
                    "class_skills": ["Concentration", "Craft", "Diplomacy", "Handle Animal", "Heal", "Knowledge (nature)", "Listen", "Profession", "Ride", "Spellcraft", "Spot", "Survival", "Swim"],
                    "spellcasting": {
                        "type": "divine",
                        "ability": "Wisdom",
                        "spells_known": "prepared"
                    },
                    "features": [
                        {"name": "Animal Companion", "level": 1, "description": "Gain a loyal animal companion"},
                        {"name": "Nature Sense", "level": 1, "description": "Bonus to Knowledge (nature) and Survival"}
                    ]
                },
                "Fighter": {
                    "name": "Fighter",
                    "description": "A versatile combatant skilled in a wide array of weapons and tactics.",
                    "hit_die": 10,
                    "base_attack_bonus": "good",
                    "saving_throws": {"Fort": "good", "Ref": "poor", "Will": "poor"},
                    "skill_points": 2,
                    "class_skills": ["Climb", "Craft", "Handle Animal", "Intimidate", "Jump", "Ride", "Swim"],
                    "spellcasting": None,
                    "features": [
                        {"name": "Bonus Feat", "level": 1, "description": "Gain a bonus feat at 1st level and every even level"}
                    ]
                },
                "Monk": {
                    "name": "Monk",
                    "description": "A martial artist who masters unarmed combat and spiritual discipline.",
                    "hit_die": 8,
                    "base_attack_bonus": "average",
                    "saving_throws": {"Fort": "good", "Ref": "good", "Will": "good"},
                    "skill_points": 4,
                    "class_skills": ["Balance", "Climb", "Concentration", "Craft", "Diplomacy", "Escape Artist", "Hide", "Jump", "Knowledge (arcana)", "Knowledge (religion)", "Listen", "Move Silently", "Perform", "Profession", "Sense Motive", "Spot", "Swim", "Tumble"],
                    "spellcasting": None,
                    "features": [
                        {"name": "Flurry of Blows", "level": 1, "description": "Extra attack with unarmed strikes"},
                        {"name": "Unarmed Strike", "level": 1, "description": "Improved unarmed damage"}
                    ]
                },
                "Paladin": {
                    "name": "Paladin",
                    "description": "A holy warrior dedicated to righteousness, wielding divine magic and smiting evil.",
                    "hit_die": 10,
                    "base_attack_bonus": "good",
                    "saving_throws": {"Fort": "good", "Ref": "poor", "Will": "poor"},
                    "skill_points": 2,
                    "class_skills": ["Concentration", "Craft", "Diplomacy", "Handle Animal", "Heal", "Knowledge (nobility)", "Knowledge (religion)", "Profession", "Ride", "Sense Motive"],
                    "spellcasting": {
                        "type": "divine",
                        "ability": "Wisdom",
                        "spells_known": "prepared"
                    },
                    "features": [
                        {"name": "Smite Evil", "level": 1, "description": "Bonus damage against evil creatures"},
                        {"name": "Divine Grace", "level": 2, "description": "Add Charisma to saves"}
                    ]
                },
                "Ranger": {
                    "name": "Ranger",
                    "description": "A skilled tracker and wilderness expert, adept at hunting specific foes.",
                    "hit_die": 8,
                    "base_attack_bonus": "good",
                    "saving_throws": {"Fort": "good", "Ref": "good", "Will": "poor"},
                    "skill_points": 6,
                    "class_skills": ["Climb", "Concentration", "Craft", "Handle Animal", "Heal", "Hide", "Jump", "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (nature)", "Listen", "Move Silently", "Profession", "Ride", "Search", "Spot", "Survival", "Swim", "Use Rope"],
                    "spellcasting": {
                        "type": "divine",
                        "ability": "Wisdom",
                        "spells_known": "prepared"
                    },
                    "features": [
                        {"name": "Favored Enemy", "level": 1, "description": "Bonus against specific creature types"},
                        {"name": "Track", "level": 1, "description": "Enhanced tracking ability"}
                    ]
                },
                "Rogue": {
                    "name": "Rogue",
                    "description": "A cunning operative skilled in stealth, traps, and precise strikes.",
                    "hit_die": 6,
                    "base_attack_bonus": "average",
                    "saving_throws": {"Fort": "poor", "Ref": "good", "Will": "poor"},
                    "skill_points": 8,
                    "class_skills": ["Appraise", "Balance", "Bluff", "Climb", "Craft", "Decipher Script", "Diplomacy", "Disable Device", "Disguise", "Escape Artist", "Forgery", "Gather Information", "Hide", "Intimidate", "Jump", "Knowledge (local)", "Listen", "Move Silently", "Open Lock", "Perform", "Profession", "Search", "Sense Motive", "Sleight of Hand", "Spot", "Swim", "Tumble", "Use Magic Device", "Use Rope"],
                    "spellcasting": None,
                    "features": [
                        {"name": "Sneak Attack", "level": 1, "description": "+1d6 damage against flanked or flat-footed enemies"},
                        {"name": "Trapfinding", "level": 1, "description": "Find and disarm traps"}
                    ]
                },
                "Sorcerer": {
                    "name": "Sorcerer",
                    "description": "An innate arcane caster who wields powerful magic through charisma and bloodline.",
                    "hit_die": 4,
                    "base_attack_bonus": "poor",
                    "saving_throws": {"Fort": "poor", "Ref": "poor", "Will": "good"},
                    "skill_points": 2,
                    "class_skills": ["Bluff", "Concentration", "Craft", "Knowledge (arcana)", "Profession", "Spellcraft"],
                    "spellcasting": {
                        "type": "arcane",
                        "ability": "Charisma",
                        "spells_known": "spontaneous"
                    },
                    "features": [
                        {"name": "Familiar", "level": 1, "description": "Gain a magical familiar"}
                    ]
                },
                "Wizard": {
                    "name": "Wizard",
                    "description": "A scholarly arcane caster who masters magic through study and spellbooks.",
                    "hit_die": 4,
                    "base_attack_bonus": "poor",
                    "saving_throws": {"Fort": "poor", "Ref": "poor", "Will": "good"},
                    "skill_points": 2,
                    "class_skills": ["Concentration", "Craft", "Decipher Script", "Knowledge (all)", "Profession", "Spellcraft"],
                    "spellcasting": {
                        "type": "arcane",
                        "ability": "Intelligence",
                        "spells_known": "prepared"
                    },
                    "features": [
                        {"name": "Spellbook", "level": 1, "description": "Prepare spells from a spellbook"},
                        {"name": "Familiar", "level": 1, "description": "Gain a magical familiar"}
                    ]
                }
            }
            with open(classes_path, 'w') as f:
                json.dump(default_classes, f, indent=2)
            logger.debug(f"Created default classes.json at {classes_path}")

    def load_classes_from_json(self) -> Dict[str, Any]:
        try:
            self.ensure_classes_file_exists()
            classes_path = self.data_dir / "classes.json"
            logger.debug(f"Attempting to load classes from {classes_path}")
            if not classes_path.exists():
                logger.error(f"Classes file not found at {classes_path}")
                return {}
            with open(classes_path) as f:
                classes_data = json.load(f)
            logger.debug(f"Loaded {len(classes_data)} classes from JSON")
            return classes_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in classes.json: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load classes from JSON: {e}")
            return {}