import random
import logging
from typing import List
from colorama import Fore, Style
from dnd_adventure.dnd35e.core.monsters import Monster, Attack

logger = logging.getLogger(__name__)

class CombatManager:
    def __init__(self, game):
        self.game = game

    def calculate_monster_difficulty(self, monster: Monster) -> float:
        hp_score = monster.hit_points
        ac_score = monster.armor_class * 2
        damage_score = 0
        if monster.attacks:
            for attack in monster.attacks:
                damage_str = attack.damage
                parts = damage_str.split('+')
                dice_part = parts[0]
                bonus = int(parts[1]) if len(parts) > 1 else 0
                num_dice, die_size = map(int, dice_part.split('d'))
                avg_damage_per_die = (1 + die_size) / 2
                avg_damage = (num_dice * avg_damage_per_die) + bonus
                damage_score += avg_damage
            damage_score *= 2
        difficulty = hp_score + ac_score + damage_score
        return max(1, difficulty)

    def calculate_xp_reward(self, monster: Monster) -> int:
        difficulty = self.calculate_monster_difficulty(monster)
        scaling_factor = 50 / 33
        xp = int(difficulty * scaling_factor)
        return max(10, xp)

    def handle_attack_command(self):
        self.game.message = ""
        logger.debug("Handling attack command")
        if not self.game.current_room:
            print("There's nothing to attack here!")
            logger.debug("No attack target: No current room")
            return
        room = self.game.game_world.rooms.get(self.game.current_room)
        if not room:
            print(f"{Fore.RED}Error: Current room {self.game.current_room} does not exist. Resetting room.{Style.RESET_ALL}")
            logger.error(f"Room not found: {self.game.current_room}")
            self.game.current_room = None
            return
        if not room.monsters:
            print("No monsters to attack!")
            logger.debug("No attack target: No monsters")
            return
        monster = room.monsters[0]
        bab = self.game.player.bab
        str_mod = self.game.player.get_stat_modifier(0)
        attack_roll = random.randint(1, 20) + bab + str_mod
        print(f"{self.game.player.name} attacks {monster.name} (Roll: {attack_roll})")
        logger.debug(f"Attack roll: {attack_roll} vs {monster.armor_class}")
        if attack_roll >= monster.armor_class:
            damage = max(1, random.randint(1, 8) + str_mod)
            monster.hit_points -= damage
            print(f"Hit! {monster.name} takes {damage} damage (HP: {monster.hit_points})")
            logger.debug(f"Hit: {monster.name} takes {damage} damage, HP now {monster.hit_points}")
            if monster.hit_points <= 0:
                print(f"{monster.name} is defeated!")
                xp_reward = self.calculate_xp_reward(monster)
                room.monsters.remove(monster)
                self.game.player.gain_xp(xp_reward)
                self.game.player_manager.check_level_up()
                logger.info(f"Defeated {monster.name}, gained {xp_reward} XP")
                if "temp_" in self.game.current_room:
                    del self.game.game_world.rooms[self.game.current_room]
                    self.game.current_room = None
                    logger.debug(f"Cleared temporary room: {self.game.current_room}")
        else:
            print("Miss!")
            logger.debug("Attack missed")
        if room.monsters:
            self.handle_monster_attack(monster)

    def handle_monster_attack(self, monster: Monster):
        if not monster.attacks:
            print(f"{monster.name} has no attacks!")
            logger.debug(f"No attacks for {monster.name}")
            return
        attack = random.choice(monster.attacks)
        attack_roll = random.randint(1, 20) + attack.attack_bonus
        print(f"{monster.name} attacks {self.game.player.name} (Roll: {attack_roll})")
        logger.debug(f"Monster attack roll: {attack_roll} vs {self.game.player.armor_class}")
        if attack_roll >= self.game.player.armor_class:
            damage_parts = attack.damage.split('+')
            dice_part = damage_parts[0]
            bonus = int(damage_parts[1]) if len(damage_parts) > 1 else 0
            num_dice, die_size = map(int, dice_part.split('d'))
            damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus
            damage = max(1, damage)
            self.game.player.hit_points -= damage
            print(f"Hit! {self.game.player.name} takes {damage} damage (HP: {self.game.player.hit_points})")
            logger.debug(f"Monster hit: {self.game.player.name} takes {damage} damage, HP now {self.game.player.hit_points}")
            if self.game.player.hit_points <= 0:
                print(f"{self.game.player.name} has been defeated!")
                logger.info(f"Player {self.game.player.name} defeated")
                self.game.running = False
        else:
            print("Miss!")
            logger.debug("Monster attack missed")

    def handle_cast_command(self, cmd: str):
        self.game.message = ""
        logger.debug(f"Handling cast command: {cmd}")
        if not self.game.current_room:
            print("There's nothing to cast spells on here!")
            logger.debug("No cast target: No current room")
            return
        room = self.game.game_world.rooms.get(self.game.current_room)
        if not room:
            print(f"{Fore.RED}Error: Current room {self.game.current_room} does not exist. Resetting room.{Style.RESET_ALL}")
            logger.error(f"Room not found: {self.game.current_room}")
            self.game.current_room = None
            return
        if not room.monsters:
            print("No monsters to cast spells on!")
            logger.debug("No cast target: No monsters")
            return
        try:
            spell_index = int(cmd.split()[-1]) - 1
            spell_list = []
            for level in sorted(self.game.player.known_spells.keys()):
                spell_list.extend(self.game.player.known_spells[level])
            if 0 <= spell_index < len(spell_list):
                spell_name = spell_list[spell_index]
                result = self.game.player.cast_spell(spell_name, room.monsters[0] if room.monsters else None)
                print(result)
                logger.debug(f"Cast spell: {spell_name}, Result: {result}")
                if "dealing" in result and room.monsters and room.monsters[0].hit_points <= 0:
                    print(f"{room.monsters[0].name} is defeated!")
                    xp_reward = self.calculate_xp_reward(room.monsters[0])
                    room.monsters.pop(0)
                    self.game.player.gain_xp(xp_reward)
                    self.game.player_manager.check_level_up()
                    logger.info(f"Defeated {room.monsters[0].name} with spell, gained {xp_reward} XP")
                    if self.game.current_room and "temp_" in self.game.current_room:
                        del self.game.game_world.rooms[self.game.current_room]
                        self.game.current_room = None
                        logger.debug(f"Cleared temporary room: {self.game.current_room}")
                if room.monsters:
                    self.handle_monster_attack(room.monsters[0])
            else:
                print("Invalid spell number!")
                logger.warning("Invalid spell number")
        except (ValueError, IndexError) as e:
            print(f"{Fore.RED}Invalid cast command. Use 'cast <number>' or 'cast list'.{Style.RESET_ALL}")
            logger.error(f"Invalid cast command: {cmd}, Error: {e}")

    def print_spell_list(self):
        self.game.message = ""
        logger.debug("Printing spell list")
        if not self.game.player.known_spells or all(len(spells) == 0 for spells in self.game.player.known_spells.values()):
            print("You don't know any spells!")
            logger.debug("No known spells")
            return
        print("\nKnown Spells:")
        spell_index = 1
        for level in sorted(self.game.player.known_spells.keys()):
            for spell in self.game.player.known_spells[level]:
                print(f"{spell_index}. Level {level}: {spell}")
                spell_index += 1
        logger.debug(f"Displayed spell list: {self.game.player.known_spells}")

    def handle_rest_command(self):
        self.game.message = ""
        logger.debug("Handling rest command")
        self.game.player.hit_points = min(self.game.player.hit_points + 10, self.game.player.max_hit_points)
        self.game.player.mp = min(self.game.player.mp + 5, self.game.player.max_mp)
        print(f"{self.game.player.name} rests, recovering to {self.game.player.hit_points} HP and {self.game.player.mp} MP.")
        logger.debug(f"Player rested: HP {self.game.player.hit_points}, MP {self.game.player.mp}")