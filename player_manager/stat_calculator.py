import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StatCalculator:
    def calculate_hp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        hit_die = class_data.get("hit_die", 6)
        con_modifier = (stat_dict.get("Constitution", 10) - 10) // 2
        hp = hit_die + con_modifier
        logger.debug(f"Calculated HP: hit_die={hit_die}, con_modifier={con_modifier}, total={hp}")
        return max(hp, 1)

    def calculate_mp(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        if not class_data.get("spellcasting"):
            logger.debug("No MP for non-spellcasting class")
            return 0
        primary_stat = class_data.get("spellcasting_stat", "Intelligence")
        stat_value = stat_dict.get(primary_stat, 10)
        mp = max((stat_value - 10) // 2, 0) * 2
        logger.debug(f"Calculated MP: primary_stat={primary_stat}, stat_value={stat_value}, mp={mp}")
        return mp

    def calculate_attack(self, class_data: Dict[str, Any], stat_dict: Dict[str, int]) -> int:
        primary_stat = class_data.get("primary_stat", "Strength")
        modifier = (stat_dict.get(primary_stat, 10) - 10) // 2
        attack = 10 + modifier
        logger.debug(f"Calculated attack: primary_stat={primary_stat}, modifier={modifier}, attack={attack}")
        return attack

    def calculate_defense(self, stat_dict: Dict[str, int]) -> int:
        dex_modifier = (stat_dict.get("Dexterity", 10) - 10) // 2
        logger.debug(f"Calculated defense: dex_modifier={dex_modifier}, defense={10 + dex_modifier}")
        return 10 + dex_modifier