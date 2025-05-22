"""
战斗单位基础模块，定义战斗系统的核心单位类。

该模块实现了Battler基类，作为游戏中所有可战斗实体（玩家、敌人、盟友等）的基础。
定义了战斗单位的共同属性和行为，包括基本属性、伤害计算、攻击机制、治疗和状态管理等。
这个基类为战斗系统提供了统一的接口和共享功能。
"""

import random
from typing import Dict
from rich.console import Console

from ui import battle_log
from ui import dot_loading, wait

console = Console()


# *基本战斗单位类
class Battler:
    """
    战斗单位基类，表示游戏中任何可参与战斗的实体。

    定义了战斗单位的基本属性和方法，包括生命值、魔法值、攻击、防御等战斗属性，
    以及攻击、受伤、防御和恢复等基本战斗行为。所有战斗单位（玩家、敌人、盟友）
    都继承自该类并可能扩展其功能。

    属性:
        name (str): 战斗单位的名称
        stats (Dict[str, int]): 战斗单位的各项属性值，如生命值、攻击力等
        alive (bool): 单位是否存活
        buffs_and_debuffs (list): 当前影响单位的增益和减益效果
        is_ally (bool): 是否为友方单位
        is_defending (bool): 是否处于防御状态
        spells (list): 单位可使用的法术列表
    """
    def __init__(self, name: str, stats: Dict[str, int]) -> None:
        """
        初始化战斗单位实例。

        设置单位的基本属性，包括名称、战斗属性和初始状态。

        参数:
            name (str): 单位名称
            stats (Dict[str, int]): 单位属性字典，包含如下键值:
                - hp: 当前生命值
                - max_hp: 最大生命值
                - mp: 当前魔法值
                - max_mp: 最大魔法值
                - atk: 物理攻击力
                - def: 物理防御力
                - mat: 魔法攻击力
                - mdf: 魔法防御力
                - agi: 敏捷（影响行动顺序和闪避）
                - luk: 幸运（影响各种随机事件）
                - crit: 暴击率
                - anti_crit: 抗暴击率
        """
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False
        self.is_defending = False
        self.spells = []

    def take_dmg(self, dmg: int) -> None:
        """
        使单位受到伤害。

        计算实际伤害值（带随机波动），应用防御状态减伤，
        减少单位生命值并检查是否死亡。

        参数:
            dmg (int): 原始伤害值

        副作用:
            - 减少单位的生命值
            - 可能改变单位的存活状态
            - 输出相关战斗信息
        """
        dmg = max(round(dmg * random.uniform(0.9, 1.1)), 5)

        if self.is_defending:
            dmg = round(dmg * 0.5)
            console.print(f"{self.name} 正在防御，伤害减半!", style="cyan")

        self.stats["hp"] -= dmg
        console.print(f"{self.name} 受到伤害 {dmg}", style="red")
        wait()
        # 检查是否死亡
        if self.stats["hp"] <= 0:
            console.print(f"{self.name} 被杀死了", style="bold red")
            self.alive = False

    def normal_attack(self, defender: 'Battler') -> int:
        """
        执行普通攻击。

        根据攻击者属性决定使用物理攻击或魔法攻击，
        检查命中、暴击等战斗机制，并应用相应伤害。

        参数:
            defender (Battler): 被攻击的目标

        返回:
            int: 造成的伤害值，未命中则为0

        副作用:
            - 目标单位受到伤害
            - 输出战斗日志和相关信息
        """
        from combat import BattleCalculator
        battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        if self.stats["mat"] > self.stats["atk"]:
            battle_log(f"{self.name} 释放了魔法攻击", "magic")
            dmg = self._calc_magic_damage(defender)
            defender.take_dmg(dmg)
            return dmg

        # 检查是否攻击未命中
        if BattleCalculator.check_miss(self,defender):
            console.print(f"{self.name} 的攻击被 {defender.name} 躲开了", style="yellow")
            return 0
        # 检查是否为暴击
        is_crit, crit_suppressed = BattleCalculator.check_critical(self, defender)
        if is_crit:
            dmg = self._calc_critical_damage(defender)
        elif crit_suppressed:
            battle_log(f"{defender.name} 回避了暴击攻击!", "info")
            dmg = self._calc_normal_damage(defender)
        else:
            dmg = self._calc_normal_damage(defender)

        defender.take_dmg(dmg)
        return dmg

    def _calc_critical_damage(self, defender: 'Battler') -> int:
        """
        计算暴击伤害。

        基于攻击者的攻击力和幸运值，以及随机暴击倍率，
        计算暴击造成的伤害值。

        参数:
            defender (Battler): 被攻击的目标

        返回:
            int: 计算后的暴击伤害值

        副作用:
            在控制台输出暴击信息
        """
        crit_base = self.stats["atk"]*3.5 + self.stats["luk"]*1.2
        rate = random.choices([1.5, 2.0, 2.5, 3.0], weights=[50, 30, 17, 3])[0] # 暴击倍率 : 概率
        rate += round(self.stats["crit"]/100, 2)
        console.print(f"暴击! x{rate}", style="bold yellow")

        dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)
        battle_log(f"{self.name} 对 {defender.name} 造成了 {dmg} 点暴击伤害", "crit")
        return dmg

    def _calc_normal_damage(self, defender):
        """
        计算普通物理攻击伤害。

        基于攻击者的攻击力和幸运值，以及防御者的防御力和幸运值，
        计算普通攻击造成的伤害值，包含±20%的随机波动。

        参数:
            defender (Battler): 被攻击的目标

        返回:
            int: 计算后的普通攻击伤害值
        """
        base = self.stats["atk"]*4 - defender.stats["def"]*2.5
        base += self.stats["luk"] - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.2) * random.uniform(0.8, 1.2)) # 伤害浮动：±20%

    def _calc_magic_damage(self, defender):
        """
        计算魔法攻击伤害。

        基于攻击者的魔法攻击力和幸运值，以及防御者的魔法防御力和幸运值，
        计算魔法攻击造成的伤害值，包含±30%的随机波动。

        参数:
            defender (Battler): 被攻击的目标

        返回:
            int: 计算后的魔法攻击伤害值
        """
        base = self.stats["mat"]*3 - defender.stats["mdf"]*1.7
        base += self.stats["luk"]*1.2 - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.5) * random.uniform(0.8, 1.3))

    def recover_mp(self, amount):
        """
        恢复魔法值。

        增加单位的当前魔法值，但不超过最大魔法值。

        参数:
            amount (int): 要恢复的魔法值数量

        副作用:
            更新单位的魔法值并输出提示信息
        """
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        console.print(f"{self.name} 恢复了 {amount}MP", style="blue")

    def heal(self, amount):
        """
        恢复生命值。

        增加单位的当前生命值，但不超过最大生命值。

        参数:
            amount (int): 要恢复的生命值数量

        副作用:
            更新单位的生命值并输出提示信息
        """
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        console.print(f"{self.name} 治愈了 {amount}HP", style="green")

    def check_buff_debuff_turns(self, clear_all: bool = False) -> None:
        """
        检查增益和减益效果的持续时间。

        遍历单位当前的所有增益和减益效果，检查其持续时间或全部清除。

        参数:
            clear_all (bool): 是否清除所有效果，默认为False

        副作用:
            可能移除已到期的增益和减益效果
        """
        for bd in self.buffs_and_debuffs:
            bd.deactivate() if clear_all else bd.check_turns()

    def defend(self):
        """
        开始防御，减少受到的伤害。

        将单位设置为防御状态，在该状态下受到的伤害将减半。

        副作用:
            - 设置单位的防御状态标志
            - 输出防御状态提示信息
        """
        self.is_defending = True
        console.print(f"{self.name} 进入防御姿态，伤害减半!", style="cyan")

    def end_defense(self):
        """
        结束防御状态。

        如果单位处于防御状态，则解除该状态。

        副作用:
            - 重置单位的防御状态标志
            - 输出状态变化提示信息
        """
        if self.is_defending:
            self.is_defending = False
            console.print(f"{self.name} 已结束防御状态。", style="cyan")
