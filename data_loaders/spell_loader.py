import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional
from dnd_adventure.spells import Spell, CORE_SPELLS
from dnd_adventure.data_loaders.data_utils import ensure_data_dir

logger = logging.getLogger(__name__)

class SpellLoader:
    def __init__(self):
        self.data_dir = ensure_data_dir()
        random.seed()

    def load_spells_from_json(self) -> Dict[str, Dict[int, List[Spell]]]:
        try:
            base_dir = Path(__file__).parent.parent
            spells_path = base_dir / "data" / "spells.json"
            logger.debug(f"Attempting to load spells from {spells_path}")
            if not spells_path.exists():
                logger.error(f"Spells file not found at {spells_path}")
                return self._load_core_spells()
            with open(spells_path) as f:
                spells_data = json.load(f)
            
            spell_dict = {}
            for class_key, data in spells_data.items():
                spell_dict[class_key] = {}
                class_stat = data.get("stat_requirement", "Intelligence" if "Wizard" in class_key else "Wisdom")
                if isinstance(class_stat, dict):
                    class_stat = class_stat.get("Wizard", "Intelligence") if "Wizard" in class_key else class_stat.get("Sorcerer", "Charisma")
                
                for level_key, spells in data.items():
                    if not level_key.startswith("level_") or not spells:
                        continue
                    level = int(level_key.replace("level_", ""))
                    spell_dict[class_key][level] = []
                    for spell in spells:
                        school = spell.get("school", spell.get("discipline", "Unknown"))
                        subschool = None
                        descriptors = []
                        if "(" in school:
                            main_school, rest = school.split(" (", 1)
                            subschool = rest.split(")")[0]
                            school = main_school
                        if "[" in school:
                            descriptors = [d.strip("[]") for d in school.split("[")[1:]]
                            descriptors = [d.split("]")[0] for d in descriptors]
                        
                        classes = {class_key: level}
                        if class_key == "Sorcerer/Wizard":
                            classes = {"Wizard": level, "Sorcerer": level}
                        
                        primary_stat = spell.get("primary_stat", class_stat)
                        stat_requirement = {
                            primary_stat: random.randint(max(6, 6 + level - 2), 6 + level)
                        }
                        logger.debug(f"Loaded spell: {spell['name']} (Level {level}, Stat Requirement: {stat_requirement})")
                        
                        min_level = spell.get("min_level", max(1, 2 * level - 1))
                        
                        spell_obj = Spell(
                            name=spell["name"],
                            level=level,
                            school=school,
                            subschool=subschool,
                            descriptor=descriptors or None,
                            casting_time=spell.get("casting_time", spell.get("manifestation_time", "1 standard action")),
                            components={
                                "verbal": spell.get("components", {}).get("verbal", True),
                                "somatic": spell.get("components", {}).get("somatic", True),
                                "material": spell.get("components", {}).get("material", False),
                                "focus": spell.get("components", {}).get("focus", False),
                                "divine_focus": spell.get("components", {}).get("divine_focus", False)
                            },
                            spell_range=spell.get("range", "Close"),
                            area=spell.get("area"),
                            target=spell.get("target"),
                            duration=spell.get("duration", "Instantaneous"),
                            saving_throw=spell.get("saving_throw"),
                            spell_resistance=spell.get("spell_resistance") == "Yes" if spell.get("spell_resistance") else None,
                            description=spell["description"],
                            classes=classes,
                            mp_cost=spell.get("mp_cost", level * 2 if level > 0 else 1),
                            min_level=min_level,
                            stat_requirement=stat_requirement,
                            primary_stat=primary_stat,
                            domain=spell.get("domain")
                        )
                        spell_dict[class_key][level].append(spell_obj)
                
                # Add Cleric domain spells
                if class_key == "Cleric" and "domains" in data:
                    for domain, domain_spells in data["domains"].items():
                        for level_key, spell_name in domain_spells.items():
                            level = int(level_key.replace("level_", ""))
                            if level not in spell_dict[class_key]:
                                spell_dict[class_key][level] = []
                            spell_obj = None
                            for cls, levels in spell_dict.items():
                                for lvl, spells in levels.items():
                                    for sp in spells:
                                        if sp.name == spell_name:
                                            spell_obj = sp
                                            break
                                    if spell_obj:
                                        break
                                if spell_obj:
                                    break
                            if spell_obj:
                                domain_spell = Spell(
                                    name=spell_obj.name,
                                    level=level,
                                    school=spell_obj.school,
                                    subschool=spell_obj.subschool,
                                    descriptor=spell_obj.descriptor,
                                    casting_time=spell_obj.casting_time,
                                    components=spell_obj.components,
                                    spell_range=spell_obj.spell_range,
                                    area=spell_obj.area,
                                    target=spell_obj.target,
                                    duration=spell_obj.duration,
                                    saving_throw=spell_obj.saving_throw,
                                    spell_resistance=spell_obj.spell_resistance,
                                    description=spell_obj.description,
                                    classes={"Cleric": level},
                                    mp_cost=spell_obj.mp_cost,
                                    min_level=spell_obj.min_level,
                                    stat_requirement={
                                        spell_obj.primary_stat: random.randint(max(6, 6 + level - 2), 6 + level)
                                    },
                                    primary_stat=spell_obj.primary_stat,
                                    domain=domain
                                )
                                spell_dict[class_key][level].append(domain_spell)
            logger.debug(f"Loaded spells for {len(spell_dict)} class groups from JSON")
            return spell_dict
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in spells.json: {e}")
            return self._load_core_spells()
        except Exception as e:
            logger.error(f"Failed to load spells from JSON: {e}")
            return self._load_core_spells()

    def _load_core_spells(self) -> Dict[str, Dict[int, List[Spell]]]:
        spell_dict = {"Sorcerer/Wizard": {0: [], 1: []}}
        for spell in CORE_SPELLS.values():
            if spell.level in [0, 1] and "Wizard" in spell.classes:
                spell_dict["Sorcerer/Wizard"][spell.level].append(spell)
        logger.debug("Loaded CORE_SPELLS as fallback")
        return spell_dict

    def get_spell_by_name(self, spell_name: str, class_name: str) -> Optional[Spell]:
        spells_data = self.load_spells_from_json()
        class_key = "Sorcerer/Wizard" if class_name in ["Wizard", "Sorcerer"] else class_name
        for level, spells in spells_data.get(class_key, {}).items():
            for spell in spells:
                if spell.name == spell_name:
                    return spell
        return CORE_SPELLS.get(spell_name)