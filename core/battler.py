import random
from typing import Dict
from rich.console import Console

import test.fx as fx
from test.combat_utils import battle_log
from test.fx import dot_loading, typewriter

console = Console()


# *基本战斗单位类
class Battler:
    def __init__(self, name: str, stats: Dict[str, int]) -> None:
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False
        self.is_defending = False
        self.spells = []

    def take_dmg(self, dmg: int) -> None:
        dmg = max(round(dmg * random.uniform(0.9, 1.1)), 5)

        if self.is_defending:
            dmg = round(dmg * 0.5)
            console.print(f"{self.name} 正在防御，伤害减半!", style="cyan")

        self.stats["hp"] -= dmg
        console.print(f"{self.name} 受到伤害 {dmg}", style="red")
        fx.wait()
        # 检查是否死亡
        if self.stats["hp"] <= 0:
            console.print(f"{self.name} 被杀死了", style="bold red")
            self.alive = False

    def normal_attack(self, defender: 'Battler') -> int:
        from combat import Battle_calculator
        battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        if self.stats["mat"] > self.stats["atk"]:
            battle_log(f"{self.name} 释放了魔法攻击", "magic")
            dmg = self._calc_magic_damage(defender)
            defender.take_dmg(dmg)
            return dmg

        # 检查是否攻击未命中
        if Battle_calculator.check_miss(self,defender):
            console.print(f"{self.name} 的攻击被 {defender.name} 躲开了", style="yellow")
            return 0
        # 检查是否为暴击
        is_crit, crit_suppressed = Battle_calculator.check_critical(self, defender)
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
        crit_base = self.stats["atk"]*3.5 + self.stats["luk"]*1.2
        rate = random.choices([1.5, 2.0, 2.5, 3.0], weights=[50, 30, 17, 3])[0] # 暴击倍率 : 概率
        rate += round(self.stats["crit"]/100, 2)
        console.print(f"暴击! x{rate}", style="bold yellow")

        dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)
        battle_log(f"{self.name} 对 {defender.name} 造成了 {dmg} 点暴击伤害", "crit")
        return dmg

    def _calc_normal_damage(self, defender):
        base = self.stats["atk"]*4 - defender.stats["def"]*2.5
        base += self.stats["luk"] - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.2) * random.uniform(0.8, 1.2)) # 伤害浮动：±20%

    def _calc_magic_damage(self, defender):
        base = self.stats["mat"]*3 - defender.stats["mdf"]*1.7
        base += self.stats["luk"]*1.2 - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.5) * random.uniform(0.8, 1.3))

    def recover_mp(self, amount):
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        typewriter(fx.blue(f"{self.name} 恢复了 {amount}MP"))

    def heal(self, amount):
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        typewriter(fx.green(f"{self.name} 治愈了 {amount}HP"))

    def check_buff_debuff_turns(self, clear_all: bool = False) -> None:
        for bd in self.buffs_and_debuffs:
            bd.deactivate() if clear_all else bd.check_turns()

    def defend(self):
        """开始防御，减少受到的伤害"""
        self.is_defending = True
        console.print(f"{self.name} 进入防御姿态，伤害减半!", style="cyan")

    def end_defense(self):
        """结束防御状态"""
        if self.is_defending:
            self.is_defending = False
            console.print(f"{self.name} 已结束防御状态。", style="cyan")
