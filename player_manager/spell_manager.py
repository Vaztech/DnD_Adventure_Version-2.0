import json
import logging
import os
from typing import Dict, List, Any
from .console_utils import console_print, console_input

logger = logging.getLogger(__name__)

class SpellManager:
    def __init__(self):
        self.default_spells = {
            "Assassin": {
                "0": [],
                "1": [
                    {"name": "Disguise Self", "description": "Changes your appearance.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Silent Image", "description": "Creates minor illusion of your design.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Ghost Sound", "description": "Creates minor sounds or music.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12}
                ]
            },
            "Wizard": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Mage Hand", "description": "5-pound telekinesis.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Intelligence", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Shield", "description": "Invisible shield gives +4 to AC, blocks magic missiles.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12},
                    {"name": "Burning Hands", "description": "1d4/level fire damage (max 5d4).", "mp_cost": 2, "primary_stat": "Intelligence", "min_level": 1, "min_stat": 12}
                ]
            },
            "Bard": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Dancing Lights", "description": "Creates torches or other lights.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Message", "description": "Whisper conversation at distance.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 damage +1/level (max +5).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Charm Person", "description": "Makes one person your friend.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12}
                ]
            },
            "Cleric": {
                "0": [
                    {"name": "Guidance", "description": "+1 on one attack roll, saving throw, or skill check.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Resistance", "description": "+1 on saving throws.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Light", "description": "Object shines like a torch.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Cure Light Wounds", "description": "Cures 1d8 damage +1/level (max +5).", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Bless", "description": "Allies gain +1 on attack rolls and saves vs fear.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12}
                ]
            },
            "Druid": {
                "0": [
                    {"name": "Flare", "description": "Dazzles one creature (-1 on attack rolls).", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10},
                    {"name": "Know Direction", "description": "You discern north.", "mp_cost": 1, "primary_stat": "Wisdom", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Entangle", "description": "Plants entangle everyone in 40-ft radius.", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12},
                    {"name": "Goodberry", "description": "2d4 berries each cure 1 hp (max 8 hp/24 hours).", "mp_cost": 2, "primary_stat": "Wisdom", "min_level": 1, "min_stat": 12}
                ]
            },
            "Sorcerer": {
                "0": [
                    {"name": "Prestidigitation", "description": "Performs minor tricks.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Acid Splash", "description": "Orb deals 1d3 acid damage.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10},
                    {"name": "Detect Magic", "description": "Detects spells and magic items within 60 ft.", "mp_cost": 1, "primary_stat": "Charisma", "min_level": 0, "min_stat": 10}
                ],
                "1": [
                    {"name": "Magic Missile", "description": "1d4+1 damage; +1 missile per two levels above 1st (max 5).", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12},
                    {"name": "Sleep", "description": "Puts 4 HD of creatures into magical slumber.", "mp_cost": 2, "primary_stat": "Charisma", "min_level": 1, "min_stat": 12}
                ]
            }
        }

    def select_spells(self, game: Any, character_class: str, player_level: int, stat_dict: Dict[str, int]) -> Dict[int, List[str]]:
        classes = game.classes
        class_data = classes.get(character_class, {})
        spells = {0: [], 1: []}
        
        if not class_data.get("spellcasting"):
            logger.debug(f"No spells available for non-spellcasting class: {character_class}")
            return spells
        
        spells_path = os.path.join(os.path.dirname(__file__), "..", "dnd_adventure", "data", "spells.json")
        try:
            with open(spells_path, "r") as f:
                spell_data = json.load(f)
            logger.debug(f"Loaded spells.json: {spell_data}")
        except FileNotFoundError:
            logger.warning(f"Spells file not found at {spells_path}, using default spells")
            spell_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding spells.json: {e}, using default spells")
            spell_data = {}
        
        # Use default_spells if spells.json is empty or lacks class spells
        available_spells = spell_data.get(character_class, self.default_spells.get(character_class, {}))
        if not available_spells:
            available_spells = self.default_spells.get(character_class, {})
            logger.warning(f"No spells defined for {character_class} in spells.json, using defaults: {available_spells}")
        
        if not available_spells:
            logger.warning(f"No spells available for {character_class} in defaults")
            console_print(f"No spells available for {character_class} at level {player_level}.", color="yellow")
            return spells
        
        logger.debug(f"Stat dict for spell selection: {stat_dict}")
        for level in [0, 1]:
            level_spells = available_spells.get(str(level), [])
            if not level_spells:
                logger.debug(f"No level {level} spells available for {character_class}")
                continue
            
            max_spells = 4 if level == 0 else 2
            eligible_spells = [
                spell for spell in level_spells
                if spell.get("min_level", 0) <= player_level and
                   stat_dict.get(spell.get("primary_stat", "Intelligence"), 10) >= spell.get("min_stat", 10)
            ]
            logger.debug(f"Eligible level {level} spells: {[s['name'] for s in eligible_spells]}")
            if not eligible_spells:
                logger.debug(f"No eligible level {level} spells for {character_class} at player level {player_level}")
                console_print(f"No level {level} spells available (check level or stat requirements).", color="yellow")
                continue
            
            console_print(f"=== Select Level {level} Spells (Choose up to {max_spells}) ===", color="cyan")
            for i, spell in enumerate(eligible_spells, 1):
                spell_name = spell.get("name", "Unknown")
                spell_desc = spell.get("description", "No description available")
                spell_mp = spell.get("mp_cost", "Unknown")
                spell_min_level = spell.get("min_level", 0)
                spell_min_stat = spell.get("min_stat", 10)
                spell_stat = spell.get("primary_stat", "Intelligence")
                console_print(f"{i}. {spell_name}", color="cyan")
                console_print(f"     Description: {spell_desc}", color="cyan")
                console_print(f"     MP Cost: {spell_mp}", color="cyan")
                console_print(f"     Min Level: {spell_min_level}", color="cyan")
                console_print(f"     Min {spell_stat}: {spell_min_stat}", color="cyan")
            console_print("----------------------------------------", color="cyan")
            
            selected = []
            while len(selected) < max_spells:
                choice = console_input(f"Select spell {len(selected)+1}/{max_spells} (number, name, or 'done' to finish): ", color="yellow").strip().lower()
                if choice == 'done' and selected:
                    break
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(eligible_spells):
                        spell_name = eligible_spells[index]["name"]
                        if spell_name not in selected:
                            selected.append(spell_name)
                            logger.debug(f"Selected spell: {spell_name}")
                        else:
                            console_print("Spell already selected. Try again.", color="red")
                    else:
                        console_print("Invalid number. Try again.", color="red")
                else:
                    choice = choice.capitalize()
                    for spell in eligible_spells:
                        spell_name = spell["name"]
                        if spell_name.lower() == choice and spell_name not in selected:
                            selected.append(spell_name)
                            logger.debug(f"Selected spell: {spell_name}")
                            break
                    else:
                        console_print("Invalid or already selected spell. Try again.", color="red")
            
            spells[level] = selected
            logger.debug(f"Selected spells for level {level}: {selected}")
        
        return spells