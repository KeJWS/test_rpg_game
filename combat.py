from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.battler import Battler

import math, random
from typing import List
from rich.console import Console

import ui.text as text
from test.combat_utils import battle_log
import test.combat_utils as utils
from test.fx import dot_loading, typewriter
from skills import enhance_weapon

console = Console()


# *战斗计算器
class Battle_calculator:
    @staticmethod
    def check_miss(attacker: Battler, defender: Battler) -> bool:
        miss_chance = math.floor(math.sqrt(max(0, 5 * defender.stats["agi"] - attacker.stats["agi"] * 2)))
        return miss_chance > random.randint(0, 100)

    @staticmethod
    def check_critical(attacker: Battler, defender: Battler) -> tuple:
        raw_chance = round(attacker.stats["crit"] * 0.8 + attacker.stats["luk"] * 0.2)
        anti_crit = defender.stats.get("anti_crit", 0)
        final_chance = max(0, min(80, raw_chance - anti_crit))

        roll = random.randint(1, 100)
        is_crit = roll <= final_chance
        was_suppressed = raw_chance > final_chance and roll <= raw_chance
        return is_crit, was_suppressed

    @staticmethod
    def try_escape(battler: Battler) -> bool:
        from skills import weakened_defense
        escape_chance = min(90, 35 + (battler.stats["agi"] * 0.7 + battler.stats["luk"] * 0.3))
        if random.randint(1, 100) <= escape_chance:
            console.print("逃跑成功!", style="green")
            return True
        console.print("逃跑失败!", style="bold red")
        if random.random() < 0.35:  # 35%概率降低防御
            console.print("你因慌乱防御力下降!", style="red")
            weakened_defense.effect(battler, battler)
        return False


# *战斗管理器
class Combat_manager:
    @staticmethod
    def define_battlers(allies: List[Battler], enemies: List[Battler]) -> List[Battler]:
        """根据速度定义行动顺序"""
        battlers = enemies.copy() + allies.copy()
        # 按敏捷排序，决定行动顺序
        return sorted(battlers, key=lambda b: b.stats["agi"], reverse=True)

    @staticmethod
    def select_target(targets: List[Battler]) -> Battler:
        """选择目标"""        
        text.select_objective(targets)
        index = utils.get_valid_input("> ", range(1, len(targets)+1), int)
        return targets[index - 1]

    @staticmethod
    def check_if_dead(allies: List[Battler], enemies: List[Battler], battlers: List[Battler]) -> None:
        """检查并移除已死亡的单位"""
        dead_bodies = [b for b in allies + enemies if not b.alive]

        for dead in dead_bodies:
            if dead in battlers:
                battlers.remove(dead)
            if dead in enemies:
                enemies.remove(dead)
            elif dead in allies:
                allies.remove(dead)

    @staticmethod
    def recover_hp_and_mp(target: Battler, percent: float) -> None:
        """按百分比恢复目标的生命值和魔法值"""
        target.stats["hp"] = min(target.stats["max_hp"], target.stats["hp"] + int(target.stats["max_hp"] * percent))
        target.stats["mp"] = min(target.stats["max_mp"], target.stats["mp"] + int(target.stats["max_mp"] * percent))
        battle_log(f"\n恢复了 {percent*100}% 生命值和魔法", "heal")


# *战斗执行器
class Combat_executor:
    def __init__(self, player, allies, enemies):
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.battlers = Combat_manager.define_battlers(allies, enemies)
        self.enemy_exp = sum(enemy.xp_reward for enemy in enemies)
        self.enemy_money = sum(enemy.gold_reward for enemy in enemies)
        self.enemy_drops = [item for enemy in enemies for item in enemy.drop_items]

    def execute_combat(self) -> bool:
        """执行战斗，返回是否逃跑"""
        print("-------------------------------------------------")
        for enemy in self.enemies:
            typewriter(f"野生的 {enemy.name} 出现了!")

        # 只要玩家存活且仍有敌人，战斗就会持续
        while self.player.alive and len(self.enemies) > 0:
            handlers = {
                "player": self._handle_player_turn,
                "ally": self._handle_ally_turn,
                "enemy": self._handle_enemy_turn
            }

            # 更新战斗顺序
            self.battlers = Combat_manager.define_battlers(self.allies, self.enemies)

            # 每个战斗单位轮流行动
            for battler in self.battlers:
                if not self.player.alive:
                    return False

                role = "player" if battler == self.player else "ally" if battler.is_ally else "enemy"
                if handlers[role](battler) is True:
                    return True

            # 回合结束，检查增益和减益的持续时间
            for battler in self.battlers:
                battler.check_buff_debuff_turns()
            text.display_status_effects(self.battlers)

        # 战斗胜利，处理奖励
        if self.player.alive:
            self._handle_combat_rewards()
            return False

    def _handle_player_turn(self, player) -> bool:
        """处理玩家的回合"""
        if player.is_defending:
            player.end_defense()

        # TODO 需要更好的自动战斗模式
        if player.auto_mode:
            text.combat_menu(player, self.allies, self.enemies)
            hp_ratio = player.stats["hp"] / player.stats["max_hp"]
            if hp_ratio < 0.3 and random.random() < 0.5:
                if Battle_calculator.try_escape(player):
                    player.check_buff_debuff_turns(True)
                    typewriter(f"{player.name} 成功逃离了战斗")
                    player.combo_points = 0
                    return True
            else:
                random_enemy = random.choice(self.enemies)
                player.normal_attack(random_enemy)
                Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)
            return False

        text.combat_menu(player, self.allies, self.enemies)
        cmd = input("> ").lower()
        while cmd not in ["a", "c", "s", "d", "e"]:
            print("请输入有效指令")
            cmd = input("> ").lower()

        if "a" in cmd:
            targeted_enemy = Combat_manager.select_target(self.enemies)
            player.normal_attack(targeted_enemy)
            Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)

        elif "s" in cmd:
            self._handle_spell_casting(player)

        elif "c" in cmd:
            self._handle_combo_usage(player)

        elif "d" in cmd:
            battle_log(f"{player.name} 正在行动。", "info")
            dot_loading()
            player.defend()
            player.add_combo_points(1)
            enhance_weapon.effect(player, player)
            console.print("你紧握武器, 时刻准备反击!", style="yellow")

        elif "e" in cmd:
            if Battle_calculator.try_escape(player):
                player.check_buff_debuff_turns(True)
                typewriter(f"{player.name} 成功逃离了战斗")
                player.combo_points = 0
                return True

        return False

    def _handle_ally_turn(self, ally):
        """处理盟友的回合"""
        if ally.is_defending:
            ally.end_defense()
        if self.enemies:
            random_enemy = random.choice(self.enemies)
            ally.normal_attack(random_enemy)
            Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_enemy_turn(self, enemy):
        """处理敌人的回合"""
        if enemy.is_defending:
            enemy.end_defense()
        if self.allies:
            decision = enemy.decide_action(self.allies)
            match decision["type"]:
                case "attack":
                    enemy.normal_attack(decision["target"])
                    Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)
                case "defend":
                    battle_log(f"{enemy.name} 正在行动", "info")
                    dot_loading()
                    enemy.defend()
                    enhance_weapon.effect(enemy, enemy)
                    console.print("敌人摆好了防御的架势!", style="yellow")
                case "spell":
                    spell = decision["spell"]
                    target = None

                    if spell.is_targeted:
                        target = random.choice(self.allies)
                    elif spell.default_target == "self":
                        target = enemy
                    elif spell.default_target == "all_enemies":
                        target = self.allies
                    elif spell.default_target == "allies":
                        target = self.enemies
                    else:
                        target = random.choice(self.allies)
                        enemy.normal_attack(target)
                        Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)
                        return

                    spell.effect(enemy, target)
                    Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_spell_casting(self, caster):
        """处理施法菜单和效果"""
        text.spell_menu(caster)
        option = int(input("> "))
        while option not in range(len(caster.spells)+1):
            print("请输入有效的数字")
            option = int(input("> "))
        if option != 0:
            spell_chosen = caster.spells[option-1]
            target = None

            if spell_chosen.is_targeted:
                target = Combat_manager.select_target(self.battlers)
            else:
                match spell_chosen.default_target:
                    case "self":
                        target = caster
                    case "all_enemies":
                        target = self.enemies
                    case "allies":
                        target = self.allies
            
            spell_chosen.effect(caster, target)
            Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_combo_usage(self, caster):
        """处理连招菜单和效果"""
        text.combo_menu(caster)
        option = int(input("> "))
        while option not in range(len(caster.combos)+1):
            print("请输入有效的数字")
            option = int(input("> "))
        if option != 0:
            combo_chosen = caster.combos[option-1]
            target = None

            if combo_chosen.is_targeted:
                target = Combat_manager.select_target(self.battlers)
            else:
                match combo_chosen.default_target:
                    case "self":
                        target = caster
                    case "all_enemies":
                        target = self.enemies

            combo_chosen.effect(caster, target)
            Combat_manager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_combat_rewards(self):
        """处理战斗结束后的奖励"""
        self.player.end_defense()
        self.player.check_buff_debuff_turns(True)
        self.player.add_exp(self.enemy_exp)
        self.player.add_money(self.enemy_money)
        self.player.combo_points = 0
        Combat_manager.recover_hp_and_mp(self.player, 0.25)

        for item in self.enemy_drops:
            self.player.inventory.add_item(item)
            print(f"- {item.name} x{item.amount}")

# *战斗入口
def combat(player, enemies):
    """战斗系统主入口"""
    allies = [player]
    combat_system = Combat_executor(player, allies, enemies)
    return combat_system.execute_combat()
