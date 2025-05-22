"""
战斗系统模块，实现游戏中的战斗机制。

该模块定义了战斗系统的核心组件，包括战斗计算器、战斗管理器和战斗执行器。
负责处理战斗中的回合制行动、伤害计算、暴击、闪避等战斗机制，
以及处理战斗奖励、逃跑尝试等功能。作为游戏的核心玩法系统之一，
提供了丰富的战斗体验和策略选择。
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.battler import Battler

import math, random
from typing import List
from rich.console import Console

import ui.text as text
from ui.combat_utils import battle_log
import ui.combat_utils as utils
from ui.fx import dot_loading, typewriter
from data.skills_data import enhance_weapon, weakened_defense

console = Console()


# *战斗计算器
class BattleCalculator:
    """
    战斗计算器类，提供战斗中各种计算的静态方法。

    负责处理战斗中的技术性计算，如命中判定、暴击判定和逃跑判定等。
    这些方法决定了战斗中的随机性和平衡性，为战斗系统提供了核心算法支持。
    """
    @staticmethod
    def check_miss(attacker: Battler, defender: Battler) -> bool:
        """
        检查攻击是否未命中。

        基于攻击者和防御者的敏捷属性计算闪避几率。
        防御者敏捷越高相对于攻击者，闪避几率越大。

        参数:
            attacker (Battler): 攻击者
            defender (Battler): 防御者

        返回:
            bool: 如果攻击未命中返回True，否则返回False
        """
        miss_chance = math.floor(math.sqrt(max(0, 5 * defender.stats["agi"] - attacker.stats["agi"] * 2)))
        return miss_chance > random.randint(0, 100)

    @staticmethod
    def check_critical(attacker: Battler, defender: Battler) -> tuple:
        """
        检查攻击是否产生暴击。

        基于攻击者的暴击属性和幸运值，以及防御者的抗暴击属性计算
        暴击几率。同时判断是否暴击被抑制。

        参数:
            attacker (Battler): 攻击者
            defender (Battler): 防御者

        返回:
            tuple: 包含两个布尔值的元组:
                - is_crit: 是否产生暴击
                - was_suppressed: 暴击是否被抑制
        """
        raw_chance = round(attacker.stats["crit"] * 0.8 + attacker.stats["luk"] * 0.2)
        anti_crit = defender.stats.get("anti_crit", 0)
        final_chance = max(0, min(80, raw_chance - anti_crit))

        roll = random.randint(1, 100)
        is_crit = roll <= final_chance
        was_suppressed = raw_chance > final_chance and roll <= raw_chance
        return is_crit, was_suppressed

    @staticmethod
    def try_escape(battler: Battler) -> bool:
        """
        尝试从战斗中逃跑。

        基于战斗单位的敏捷和幸运属性计算逃跑成功率。
        逃跑失败有一定概率导致单位防御力下降。

        参数:
            battler (Battler): 尝试逃跑的战斗单位

        返回:
            bool: 如果逃跑成功返回True，否则返回False

        副作用:
            逃跑失败时有35%概率降低单位的防御力
        """
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
class CombatManager:
    """
    战斗管理器类，提供战斗流程管理的静态方法。

    负责处理战斗单位的行动顺序、目标选择、死亡检查和恢复处理等功能。
    作为战斗系统的协调组件，管理战斗中的各种状态和流程。
    """
    @staticmethod
    def define_battlers(allies: List[Battler], enemies: List[Battler]) -> List[Battler]:
        """
        根据速度定义行动顺序。

        将所有战斗单位合并并按敏捷属性排序，决定回合中的行动顺序。

        参数:
            allies (List[Battler]): 友方单位列表
            enemies (List[Battler]): 敌方单位列表

        返回:
            List[Battler]: 按敏捷排序的所有战斗单位列表
        """
        battlers = enemies.copy() + allies.copy()
        # 按敏捷排序，决定行动顺序
        return sorted(battlers, key=lambda b: b.stats["agi"], reverse=True)

    @staticmethod
    def select_target(targets: List[Battler]) -> Battler:
        """
        选择战斗目标。

        显示可选目标列表并允许用户选择一个作为目标。

        参数:
            targets (List[Battler]): 可选目标的列表

        返回:
            Battler: 选择的目标单位
        """
        text.select_objective(targets)
        index = utils.get_valid_input("> ", range(1, len(targets)+1), int)
        return targets[index - 1]

    @staticmethod
    def check_if_dead(allies: List[Battler], enemies: List[Battler], battlers: List[Battler]) -> None:
        """
        检查并移除已死亡的单位。

        遍历所有战斗单位，将已死亡的单位从各个列表中移除。

        参数:
            allies (List[Battler]): 友方单位列表
            enemies (List[Battler]): 敌方单位列表
            battlers (List[Battler]): 所有战斗单位列表

        副作用:
            从各个列表中移除已死亡的单位
        """
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
        """
        按百分比恢复目标的生命值和魔法值。

        根据目标最大生命值和魔法值的百分比恢复当前值。

        参数:
            target (Battler): 要恢复的目标单位
            percent (float): 恢复的百分比，如0.25表示恢复25%

        副作用:
            更新目标的生命值和魔法值
            在战斗日志中记录恢复事件
        """
        target.stats["hp"] = min(target.stats["max_hp"], target.stats["hp"] + int(target.stats["max_hp"] * percent))
        target.stats["mp"] = min(target.stats["max_mp"], target.stats["mp"] + int(target.stats["max_mp"] * percent))
        battle_log(f"\n恢复了 {percent*100}% 生命值和魔法", "heal")


# *战斗执行器
class CombatExecutor:
    """
    战斗执行器类，负责执行完整的战斗流程。

    管理战斗的整个生命周期，包括初始化战斗、执行回合、处理各种行动和结算战斗结果。
    作为战斗系统的主要控制器，协调各战斗单位的行动和战斗状态的变化。
    """
    def __init__(self, player, allies, enemies):
        """
        初始化战斗执行器。

        设置战斗的初始状态，包括参与战斗的单位、战斗顺序和可能的奖励。

        参数:
            player: 玩家对象
            allies: 友方单位列表，包括玩家
            enemies: 敌方单位列表
        """
        self.player = player
        self.allies = allies
        self.enemies = enemies
        self.battlers = CombatManager.define_battlers(allies, enemies)
        self.enemy_exp = sum(enemy.xp_reward for enemy in enemies)
        self.enemy_money = sum(enemy.gold_reward for enemy in enemies)

    def execute_combat(self) -> bool:
        """
        执行完整的战斗流程。

        控制战斗的主循环，处理每个单位的回合，检查战斗状态，并在战斗结束时处理奖励。

        返回:
            bool: 如果战斗由于逃跑而结束返回True，其他情况返回False
        """
        enemy_drops = [item for enemy in self.enemies for item in enemy.drop_items]

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
            self.battlers = CombatManager.define_battlers(self.allies, self.enemies)

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
            self._handle_combat_rewards(enemy_drops)
            return False

    def _handle_player_turn(self, player) -> bool:
        """
        处理玩家的回合。

        显示战斗菜单并处理玩家的行动选择，包括普通攻击、施法、使用连招、
        防御或尝试逃跑。支持自动战斗模式。

        参数:
            player: 玩家对象

        返回:
            bool: 如果玩家成功逃跑返回True，否则返回False
        """
        if player.is_defending:
            player.end_defense()

        # TODO 需要更好的自动战斗模式
        if player.auto_mode:
            text.combat_menu(player, self.allies, self.enemies)
            hp_ratio = player.stats["hp"] / player.stats["max_hp"]
            if hp_ratio < 0.3 and random.random() < 0.5:
                if BattleCalculator.try_escape(player):
                    player.check_buff_debuff_turns(True)
                    typewriter(f"{player.name} 成功逃离了战斗")
                    player.combo_points = 0
                    return True
            else:
                random_enemy = random.choice(self.enemies)
                player.normal_attack(random_enemy)
                CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)
            return False

        text.combat_menu(player, self.allies, self.enemies)
        cmd = input("> ").lower()
        while cmd not in ["a", "c", "s", "d", "q"]:
            print("请输入有效指令")
            cmd = input("> ").lower()

        if "a" in cmd:
            targeted_enemy = CombatManager.select_target(self.enemies)
            player.normal_attack(targeted_enemy)
            CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)

        elif "s" in cmd:
            self._handle_spell_casting(player)

        elif "c" in cmd:
            self._handle_combo_usage(player)

        elif "d" in cmd:
            battle_log(f"{player.name} 正在行动。", "info")
            dot_loading()
            player.defend()
            player.combo_points += 1
            enhance_weapon.effect(player, player)
            console.print("你紧握武器, 时刻准备反击!", style="yellow")

        elif "q" in cmd:
            if BattleCalculator.try_escape(player):
                player.check_buff_debuff_turns(True)
                typewriter(f"{player.name} 成功逃离了战斗")
                player.combo_points = 0
                return True

        return False

    def _handle_ally_turn(self, ally):
        """
        处理盟友的回合。

        自动控制盟友单位的行动，目前只实现了对随机敌人的基本攻击。

        参数:
            ally: 盟友单位
        """
        if ally.is_defending:
            ally.end_defense()
        if self.enemies:
            random_enemy = random.choice(self.enemies)
            ally.normal_attack(random_enemy)
            CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_enemy_turn(self, enemy):
        """
        处理敌人的回合。

        根据敌人的AI决策执行相应行动，可能是攻击、防御或施法。

        参数:
            enemy: 敌人单位
        """
        if enemy.is_defending:
            enemy.end_defense()
        if self.allies:
            decision = enemy.decide_action(self.allies)
            match decision["type"]:
                case "attack":
                    enemy.normal_attack(decision["target"])
                    CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)
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
                        CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)
                        return

                    spell.effect(enemy, target)
                    CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_spell_casting(self, caster):
        """
        处理施法菜单和效果。

        显示施法者可用的法术列表，允许选择并施放法术。
        根据法术的目标类型选择适当的目标。

        参数:
            caster: 施法者单位
        """
        text.spell_menu(caster)
        option = int(input("> "))
        while option not in range(len(caster.spells)+1):
            print("请输入有效的数字")
            option = int(input("> "))
        if option != 0:
            spell_chosen = caster.spells[option-1]
            target = None

            if spell_chosen.is_targeted:
                target = CombatManager.select_target(self.battlers)
            else:
                match spell_chosen.default_target:
                    case "self":
                        target = caster
                    case "all_enemies":
                        target = self.enemies
                    case "allies":
                        target = self.allies

            spell_chosen.effect(caster, target)
            CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_combo_usage(self, caster):
        """
        处理连招菜单和效果。

        显示施法者可用的连招列表，允许选择并使用连招。
        根据连招的目标类型选择适当的目标。

        参数:
            caster: 使用连招的单位
        """
        text.combo_menu(caster)
        option = int(input("> "))
        while option not in range(len(caster.combos)+1):
            print("请输入有效的数字")
            option = int(input("> "))
        if option != 0:
            combo_chosen = caster.combos[option-1]
            target = None

            if combo_chosen.is_targeted:
                target = CombatManager.select_target(self.battlers)
            else:
                match combo_chosen.default_target:
                    case "self":
                        target = caster
                    case "all_enemies":
                        target = self.enemies

            combo_chosen.effect(caster, target)
            CombatManager.check_if_dead(self.allies, self.enemies, self.battlers)

    def _handle_combat_rewards(self, enemy_drops):
        """
        处理战斗结束后的奖励。

        在战斗胜利后发放经验、金钱和物品奖励，同时恢复部分生命值和魔法值。

        参数:
            enemy_drops: 敌人掉落的物品列表

        副作用:
            - 添加经验和金钱给玩家
            - 将掉落物品添加到玩家库存
            - 恢复玩家部分生命值和魔法值
            - 重置玩家的连击点数
        """
        self.player.end_defense()
        self.player.check_buff_debuff_turns(True)
        self.player.add_exp(self.enemy_exp)
        self.player.add_money(self.enemy_money)
        self.player.combo_points = 0
        CombatManager.recover_hp_and_mp(self.player, 0.25)

        for item in enemy_drops:
            self.player.inventory.add_item(item)
            print(f"- {item.name} x{item.amount}")

# *战斗入口
def combat(player, enemies):
    """
    战斗系统主入口。

    创建战斗执行器并启动战斗流程。这是游戏其他部分调用战斗系统的主要接口。

    参数:
        player: 玩家对象
        enemies: 敌人单位列表

    返回:
        bool: 如果战斗由于逃跑而结束返回True，战斗结束返回False
    """
    allies = [player]
    combat_system = CombatExecutor(player, allies, enemies)
    return combat_system.execute_combat()
