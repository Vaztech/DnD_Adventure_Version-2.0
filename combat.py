from typing import Dict, Union, List
import random
import logging

# Local imports - using consistent absolute imports
from dnd_adventure.character import Character
from dnd_adventure.dnd35e.core.monsters import Monster, SRD_MONSTERS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CombatSystem:
    """Combat system for resolving attacks and monster abilities."""

    def __init__(self):
        logger.debug(f"Using Character class from: {Character.__module__}")

    @staticmethod
    def determine_initiative(combatants: List[Union[Character, Monster]]) -> List[Union[Character, Monster]]:
        """
        Roll initiative for each combatant using Dexterity modifiers.
        Returns combatants sorted by highest initiative first.
        """
        initiative_rolls = []
        for c in combatants:
            dex = c.ability_scores.dexterity if isinstance(c, Character) else c.abilities.get('DEX', 10)
            mod = (dex - 10) // 2
            roll = random.randint(1, 20) + mod
            initiative_rolls.append((roll, c))
            logger.info(f"Initiative: {getattr(c, 'name', 'Monster')} rolled {roll} (DEX mod {mod})")

        return [c for _, c in sorted(initiative_rolls, key=lambda x: x[0], reverse=True)]

    @staticmethod
    def resolve_attack(attacker: Union[Character, Monster], 
                       defender: Union[Character, Monster],
                       attack_name: str = None) -> Dict:
        """
        Resolve a combat attack with full monster capabilities.
        Returns a dictionary with the results.
        """
        result = {
            'attacker': getattr(attacker, 'name', 'Unknown Attacker'),
            'defender': getattr(defender, 'name', 'Unknown Defender'),
            'hit': False,
            'critical': False,
            'damage': 0,
            'special_effects': [],
            'status_effects_applied': [],
            'error': None,
        }

        # Determine attack bonus, damage, and modifier
        if isinstance(attacker, Character):
            attack_bonus = attacker.attack_bonus()
            weapon = getattr(attacker, 'get_equipped_weapon', lambda: None)()
            damage_dice = weapon.dnd_item.damage if weapon else "1d3"
            damage_mod = attacker.ability_scores.get_modifier('strength')
            special = getattr(weapon.dnd_item, 'special', None) if weapon else None
        else:
            attack = None
            if attack_name:
                attack = next((a for a in attacker.attacks if a.name.lower() == attack_name.lower()), None)
            if not attack and hasattr(attacker, 'attacks'):
                attack = attacker.attacks[0] if attacker.attacks else None
            if not attack:
                result['error'] = "No valid attack found."
                return result

            attack_bonus = attack.attack_bonus
            damage_dice = attack.damage
            damage_mod = (attacker.abilities.get('STR', 10) - 10) // 2
            special = getattr(attack, 'special', None)

        # Roll attack
        attack_roll = random.randint(1, 20)
        is_critical = attack_roll == 20
        result['attack_roll'] = attack_roll
        result['attack_bonus'] = attack_bonus

        # Defender AC check
        defender_ac = getattr(defender, 'armor_class', lambda: 10)()
        if is_critical or (attack_roll + attack_bonus) >= defender_ac:
            result['hit'] = True
            result['critical'] = is_critical

            # Calculate damage
            damage = CombatSystem.roll_dice(damage_dice) + damage_mod
            if is_critical:
                damage *= 2
            result['damage'] = max(1, damage)

            # Special effects
            if special:
                result['special_effects'].append(special)
                if hasattr(defender, 'apply_status') and isinstance(special, str):
                    defender.apply_status(special)
                    result['status_effects_applied'].append(special)

        return result

    @staticmethod
    def roll_dice(dice_str: str) -> int:
        """Dice roller that supports complex expressions (e.g., 2d6+3)."""
        try:
            if '+' in dice_str:
                return sum(CombatSystem._roll_dice_part(p) for p in dice_str.split('+'))
            elif '-' in dice_str:
                parts = dice_str.split('-')
                return CombatSystem._roll_dice_part(parts[0]) - sum(CombatSystem._roll_dice_part(p) for p in parts[1:])
            else:
                return CombatSystem._roll_dice_part(dice_str)
        except Exception as e:
            logger.error(f"Dice rolling error: {e}")
            return 0

    @staticmethod
    def _roll_dice_part(part: str) -> int:
        """Parse individual dice parts."""
        part = part.strip()
        if 'd' in part:
            try:
                num, sides = map(int, part.split('d'))
                return sum(random.randint(1, sides) for _ in range(num))
            except Exception as e:
                logger.error(f"Roll error in part '{part}': {e}")
                return 0
        else:
            try:
                return int(part)
            except ValueError:
                return 0

    @staticmethod
    def resolve_monster_abilities(monster: Monster) -> Dict:
        """Select spell-like or special abilities to activate."""
        abilities_used = {}

        # Spell-like
        if hasattr(monster, 'spell_like_abilities'):
            for ability, uses in monster.spell_like_abilities.items():
                if uses == 'At will' or random.random() > 0.7:
                    abilities_used[ability] = {
                        'type': 'spell-like',
                        'dc': getattr(monster, 'spell_dc', 10 + (monster.abilities.get('CHA', 10) - 10) // 2)
                    }

        # Special attacks
        for ability in getattr(monster, 'abilities_list', []):
            if ability.uses == 'At will' or random.random() > 0.7:
                abilities_used[ability.name] = {
                    'type': 'special',
                    'description': ability.description,
                    'dc': getattr(ability, 'dc', 10)
                }

        return abilities_used