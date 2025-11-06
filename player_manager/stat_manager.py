import logging
import random
from typing import Optional, List, Dict
from .console_utils import console_print, console_input
from .race_manager import RaceManager

logger = logging.getLogger(__name__)

class StatManager:
    def __init__(self):
        self.point_buy_costs = {
            4: -2, 5: -1, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6,
            13: 8, 14: 10, 15: 12, 16: 15, 17: 18, 18: 21
        }
        self.stat_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        self.stat_descriptions = [
            "Affects melee attack and damage, carrying capacity.",
            "Affects AC, ranged attacks, Reflex saves, Stealth.",
            "Affects HP, Fortitude saves, endurance.",
            "Affects Wizard spells, skill points, Knowledge.",
            "Affects Cleric/Druid spells, Will saves, Perception.",
            "Affects Sorcerer/Bard spells, social skills, leadership."
        ]
        self.preferred_stats = {
            "Barbarian": "Strength",
            "Bard": "Charisma",
            "Cleric": "Wisdom",
            "Druid": "Wisdom",
            "Fighter": "Strength",
            "Monk": "Dexterity",
            "Paladin": "Charisma",
            "Ranger": "Dexterity",
            "Rogue": "Dexterity",
            "Sorcerer": "Charisma",
            "Wizard": "Intelligence",
            "Assassin": "Dexterity"
        }

    def choose_stats(self, race: str, subrace: Optional[str], character_class: str) -> List[int]:
        race_manager = RaceManager()
        while True:
            console_print("=== Select Stat Allocation Method ===", color="cyan")
            console_print("1. Random Allocation", color="cyan")
            console_print("     Randomly allocate 30 points (min 1, max 12 before modifiers).", color="cyan")
            console_print("2. Allocate Points Manually", color="cyan")
            console_print("     Distribute 25 points (start at 6, min 4, max 15 before modifiers).", color="cyan")
            if character_class == "Wizard":
                console_print("Note: Wizards benefit from high Intelligence (12+ recommended for level 1 spells).", color="yellow")
            console_print("----------------------------------------", color="cyan")
            choice = console_input("Select method (1-2): ", color="yellow").strip()
            
            logger.debug(f"Selected stat method: {choice}")
            if choice == "1":
                while True:
                    stats = self._allocate_stats(race, subrace, character_class, point_pool=30, random_allocation=True)
                    console_print("Generated Stats:", color="cyan")
                    for stat, value in zip(self.stat_names, stats):
                        console_print(f"{stat}: {value}", color="cyan")
                    accept = console_input("Accept stats? (yes/no): ", color="yellow").strip().lower()
                    if accept == "yes":
                        return stats
                    elif accept != "no":
                        console_print("Please enter 'yes' or 'no'.", color="red")
            elif choice == "2":
                return self._allocate_stats(race, subrace, character_class, point_pool=25, random_allocation=False)
            console_print("Invalid choice. Please select 1 or 2.", color="red")

    def _allocate_stats(self, race: str, subrace: Optional[str], character_class: str, point_pool: int, random_allocation: bool) -> List[int]:
        race_manager = RaceManager()
        min_stat = 1 if random_allocation else 4
        max_stat = 12 if random_allocation else 15
        base_stat = 1 if random_allocation else 6
        stats = [base_stat] * 6
        unallocated_points = point_pool
        
        race_dict = race_manager.get_race_data(race)
        subrace_dict = race_dict.get("subraces", {}).get(subrace, {}) if subrace else {}
        race_modifiers = race_dict.get("ability_modifiers", {})
        subrace_modifiers = subrace_dict.get("ability_modifiers", {})
        combined_modifiers = {}
        for stat, value in race_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
        for stat, value in subrace_modifiers.items():
            combined_modifiers[stat] = combined_modifiers.get(stat, 0) + value
        
        preferred_stat = self.preferred_stats.get(character_class, "Intelligence")
        preferred_stat_idx = self.stat_names.index(preferred_stat)
        
        if random_allocation:
            preferred_value = min(12, max(10, random.randint(8, 12)))
            stats[preferred_stat_idx] = preferred_value
            unallocated_points -= self.point_buy_costs.get(preferred_value, 0)
            possible_values = [v for v in self.point_buy_costs.keys() if min_stat <= v <= max_stat]
            weights = [1 if v < 8 else 3 for v in possible_values]
            while unallocated_points > 0:
                stat_idx = random.randint(0, 5)
                if stats[stat_idx] >= max_stat:
                    continue
                next_values = [v for v in possible_values if v > stats[stat_idx] and self.point_buy_costs[v] - self.point_buy_costs.get(stats[stat_idx], 0) <= unallocated_points]
                if not next_values:
                    continue
                new_value = random.choices(next_values, weights[:len(next_values)], k=1)[0]
                cost = self.point_buy_costs[new_value] - self.point_buy_costs.get(stats[stat_idx], 0)
                stats[stat_idx] = new_value
                unallocated_points -= cost
            logger.debug(f"Randomly allocated stats: {stats}, remaining points: {unallocated_points}")
            return stats
        
        def get_cost_to_increment(current_value: int) -> Optional[int]:
            if current_value >= max_stat:
                return None
            next_value = current_value + 1
            return self.point_buy_costs.get(next_value, float('inf')) - self.point_buy_costs.get(current_value, 0)
        
        while True:
            console_print("=== Manual Stat Allocation ===", color="cyan")
            console_print(f"Unallocated points: {unallocated_points}", color="cyan")
            console_print(f"Racial Modifiers: {race_manager.format_modifiers(combined_modifiers) or 'None'}", color="cyan")
            for i, (stat_name, value, desc) in enumerate(zip(self.stat_names, stats, self.stat_descriptions), 1):
                base_modifier = (value - 10) // 2
                racial_mod = combined_modifiers.get(stat_name, 0)
                final_value = value + racial_mod
                final_modifier = (final_value - 10) // 2
                cost_to_next = get_cost_to_increment(value)
                cost_str = f"To increase to {value + 1}: {cost_to_next} point{'s' if cost_to_next != 1 else ''}" if cost_to_next is not None else "Maxed out"
                console_print(f"{i}. {stat_name}: {value} ({'+' if base_modifier >= 0 else ''}{base_modifier})", color="cyan")
                if racial_mod:
                    console_print(f"     With racial ({'+' if racial_mod > 0 else ''}{racial_mod}): {final_value} ({'+' if final_modifier >= 0 else ''}{final_modifier})", color="cyan")
                console_print(f"     {desc}", color="cyan")
                console_print(f"     {cost_str}", color="cyan")
            selection = console_input("Select stat (1-6) or 'done' to finalize: ", color="yellow").strip().lower()
            
            if selection == "done":
                if unallocated_points > 0:
                    console_print(f"Cannot finalize: {unallocated_points} points remain unallocated. Spend them or lose them.", color="red")
                    finalize = console_input("Finalize anyway? (yes/no): ", color="yellow").strip().lower()
                    if finalize == "yes":
                        logger.debug(f"Finalized stats: {stats}, unused points: {unallocated_points}")
                        return stats
                    elif finalize != "no":
                        console_print("Please enter 'yes' or 'no'.", color="red")
                    continue
                finalize = console_input("Finalize stats? (yes/no): ", color="yellow").strip().lower()
                if finalize == "yes":
                    logger.debug(f"Finalized stats: {stats}")
                    return stats
                elif finalize != "no":
                    console_print("Please enter 'yes' or 'no'.", color="red")
                continue
            
            if not selection.isdigit() or not 1 <= int(selection) <= 6:
                console_print("Invalid input. Please select a number (1-6) or 'done'.", color="red")
                continue
            
            stat_idx = int(selection) - 1
            prompt = f"Enter target value for {self.stat_names[stat_idx]} ({min_stat}-{max_stat}) or '+n'/'-n' to adjust (e.g., '+2', '-1'): "
            input_str = console_input(prompt, color="yellow").strip()
            
            try:
                if input_str.startswith('+') or input_str.startswith('-'):
                    points = int(input_str)
                    target_value = stats[stat_idx] + points
                else:
                    target_value = int(input_str)
                
                if target_value < min_stat or target_value > max_stat:
                    console_print(f"Value must be between {min_stat} and {max_stat}.", color="red")
                    continue
                
                cost = self.point_buy_costs.get(target_value, float('inf'))
                current_cost = self.point_buy_costs.get(stats[stat_idx], 0)
                cost_difference = cost - current_cost
                
                if cost_difference > unallocated_points:
                    console_print(f"Not enough points ({unallocated_points} available, need {cost_difference}).", color="red")
                    continue
                if cost_difference < 0 and abs(cost_difference) > point_pool - unallocated_points:
                    console_print("Cannot remove more points than allocated.", color="red")
                    continue
                
                stats[stat_idx] = target_value
                unallocated_points -= cost_difference
                logger.debug(f"Updated {self.stat_names[stat_idx]} to {stats[stat_idx]}, unallocated points: {unallocated_points}")
            except ValueError:
                console_print(f"Invalid input. Enter a number ({min_stat}-{max_stat}) or '+n'/'-n' (e.g., '+2').", color="red")