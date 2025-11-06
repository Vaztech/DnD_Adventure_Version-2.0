import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dnd_adventure.race_models import Race
from dnd_adventure.spells import Spell

logger = logging.getLogger(__name__)

class DataLoader:
    def ensure_data_files_exist(self) -> None:
        base_dir = Path(__file__).parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        races_path = data_dir / "races.json"
        if not races_path.exists():
            default_races = [
                {
                    "name": "Human",
                    "description": "Versatile and adaptable, humans excel in any profession through determination and ingenuity.",
                    "ability_modifiers": {},
                    "size": "Medium",
                    "speed": 30,
                    "racial_traits": [
                        {
                            "name": "Bonus Feat",
                            "description": "Gain one extra feat at 1st level"
                        },
                        {
                            "name": "Extra Skills",
                            "description": "Gain 4 extra skill points at 1st level and 1 extra skill point at each additional level"
                        }
                    ],
                    "favored_class": "Any",
                    "languages": ["Common"],
                    "subraces": {}
                },
                {
                    "name": "Elf",
                    "description": "Graceful and magical, elves are attuned to nature and arcane arts, with keen senses and natural affinity for archery.",
                    "ability_modifiers": {"Dexterity": 2, "Constitution": -2},
                    "size": "Medium",
                    "speed": 30,
                    "racial_traits": [
                        {
                            "name": "Low-Light Vision",
                            "description": "Can see twice as far as a human in dim light"
                        },
                        {
                            "name": "Keen Senses",
                            "description": "+2 bonus on Listen, Search, and Spot checks"
                        },
                        {
                            "name": "Immunity to Sleep",
                            "description": "Immune to magical sleep effects"
                        },
                        {
                            "name": "Elven Weapon Proficiency",
                            "description": "Proficient with longsword, rapier, longbow, shortbow, and composite versions"
                        }
                    ],
                    "favored_class": "Wizard",
                    "languages": ["Common", "Elven", "Sylvan"],
                    "subraces": {
                        "High Elf": {
                            "description": "Skilled in arcane magic and intellectual pursuits.",
                            "ability_modifiers": {"Intelligence": 1},
                            "racial_traits": [
                                {
                                    "name": "Arcane Focus",
                                    "description": "+2 bonus on Spellcraft checks related to arcane magic"
                                }
                            ]
                        },
                        "Wood Elf": {
                            "description": "Swift and stealthy, masters of forest navigation.",
                            "ability_modifiers": {"Wisdom": 1},
                            "racial_traits": [
                                {
                                    "name": "Forest Stride",
                                    "description": "Move through natural undergrowth at normal speed"
                                }
                            ]
                        },
                        "Dark Elf (Drow)": {
                            "description": "Cunning and shadowy, with innate magical abilities and darkvision.",
                            "ability_modifiers": {"Charisma": 1},
                            "racial_traits": [
                                {
                                    "name": "Spell Resistance",
                                    "description": "Spell Resistance equal to 11 + class levels"
                                },
                                {
                                    "name": "Superior Darkvision",
                                    "description": "Can see in the dark up to 120 feet"
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "Dwarf",
                    "description": "Sturdy and resilient, dwarves are masters of stone and metal, with a deep connection to craftsmanship.",
                    "ability_modifiers": {"Constitution": 2, "Charisma": -2},
                    "size": "Medium",
                    "speed": 20,
                    "racial_traits": [
                        {
                            "name": "Darkvision (60 ft)",
                            "description": "Can see in the dark up to 60 feet"
                        },
                        {
                            "name": "Stability",
                            "description": "+4 bonus against bull rush or trip attempts when standing on the ground"
                        },
                        {
                            "name": "Stonecunning",
                            "description": "+2 bonus on Search checks related to stonework"
                        },
                        {
                            "name": "Poison Resistance",
                            "description": "+2 bonus on saving throws against poison"
                        }
                    ],
                    "favored_class": "Fighter",
                    "languages": ["Common", "Dwarven"],
                    "subraces": {
                        "Hill Dwarf": {
                            "description": "Hardy and wise, with strong community ties.",
                            "ability_modifiers": {"Wisdom": 1},
                            "racial_traits": [
                                {
                                    "name": "Resilient",
                                    "description": "Gain +2 on saving throws against poison and spells"
                                }
                            ]
                        },
                        "Mountain Dwarf": {
                            "description": "Tough and martial, skilled in combat.",
                            "ability_modifiers": {"Strength": 1},
                            "racial_traits": [
                                {
                                    "name": "Armor Training",
                                    "description": "Proficient with light and medium armor"
                                }
                            ]
                        }
                    }
                }
            ]
            with open(races_path, 'w') as f:
                json.dump(default_races, f, indent=2)
            logger.debug(f"Created default races.json at {races_path}")

        classes_path = data_dir / "classes.json"
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

    def load_races_from_json(self) -> List[Race]:
        try:
            self.ensure_data_files_exist()
            base_dir = Path(__file__).parent
            races_path = base_dir / "data" / "races.json"
            logger.debug(f"Attempting to load races from {races_path}")
            if not races_path.exists():
                logger.error(f"Races file not found at {races_path}")
                return []
            with open(races_path) as f:
                races_data = json.load(f)
            logger.debug(f"Loaded {len(races_data)} races from JSON")
            return [Race(**race) for race in races_data]
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in races.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load races from JSON: {e}")
            return []

    def load_classes_from_json(self) -> Dict[str, Any]:
        try:
            self.ensure_data_files_exist()
            base_dir = Path(__file__).parent
            classes_path = base_dir / "data" / "classes.json"
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

    def load_spells_from_json(self) -> Dict[str, Dict[int, List[Spell]]]:
        try:
            self.ensure_data_files_exist()
            base_dir = Path(__file__).parent
            spells_path = base_dir / "data" / "spells.json"
            logger.debug(f"Attempting to load spells from {spells_path}")
            if not spells_path.exists():
                logger.error(f"Spells file not found at {spells_path}")
                return {}
            with open(spells_path) as f:
                spells_data = json.load(f)
            
            spell_dict = {}
            for class_key, levels in spells_data.items():
                spell_dict[class_key] = {}
                for level_key, spells in levels.items():
                    level = int(level_key.replace("level_", ""))
                    spell_dict[class_key][level] = []
                    for spell in spells:
                        # Parse school for subschool and descriptors
                        school = spell["school"]
                        subschool = None
                        descriptors = []
                        if "(" in school:
                            main_school, rest = school.split(" (", 1)
                            subschool = rest.split(")")[0]
                            school = main_school
                        if "[" in spell["school"]:
                            descriptors = [d.strip("[]") for d in spell["school"].split("[")[1:]]
                            descriptors = [d.split("]")[0] for d in descriptors]
                        
                        # Map class_key to classes dictionary
                        classes = {class_key: level}
                        if class_key == "Sorcerer/Wizard":
                            classes = {"Wizard": level, "Sorcerer": level}
                        
                        spell_obj = Spell(
                            name=spell["name"],
                            level=level,
                            school=school,
                            subschool=subschool,
                            descriptor=descriptors or None,
                            casting_time=spell.get("casting_time", "1 standard action"),
                            components={
                                "verbal": True,
                                "somatic": True,
                                "material": False,
                                "focus": False,
                                "divine_focus": False
                            },
                            spell_range=spell.get("range", "Close"),
                            area=spell.get("area"),
                            target=spell.get("target"),
                            duration=spell.get("duration", "Instantaneous"),
                            saving_throw=spell.get("saving_throw"),
                            spell_resistance=spell.get("spell_resistance") == "Yes" if spell.get("spell_resistance") else None,
                            description=spell["description"],
                            classes=classes
                        )
                        spell_dict[class_key][level].append(spell_obj)
            logger.debug(f"Loaded spells for {len(spell_dict)} class groups from JSON")
            return spell_dict
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in spells.json: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load spells from JSON: {e}")
            return {}

    def get_spell_by_name(self, spell_name: str, class_name: str) -> Optional[Spell]:
        spells_data = self.load_spells_from_json()
        class_key = "Sorcerer/Wizard" if class_name in ["Wizard", "Sorcerer"] else class_name
        for level, spells in spells_data.get(class_key, {}).items():
            for spell in spells:
                if spell.name == spell_name:
                    return spell
        return None