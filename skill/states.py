from typing import TYPE_CHECKING
from rich.console import Console

if TYPE_CHECKING:
    from core.battler import Battler

console = Console()

class BuffDebuff:
    """
    增益/减益状态类，用于管理临时改变战斗单位属性的效果。

    实现了对战斗单位某个属性的临时修改，持续指定回合数后自动移除。

    属性:
        name (str): 效果名称
        target (Battler): 效果目标
        stat (str): 被修改的属性名称
        amount (float): 属性变化的百分比
        turns (int): 当前剩余回合数
        max_turns (int): 初始效果持续回合数
        effect_type: 效果类型标识
        difference (int): 属性实际变化的数值
    """
    def __init__(self, name, target: "Battler", stat, amount, turns, effect_type=None):
        """
        初始化增益/减益状态实例。

        设置状态的基本属性，包括名称、目标、修改的属性和变化量等。

        参数:
            name (str): 效果名称
            target (Battler): 效果目标
            stat (str): 要修改的属性名称
            amount (float): 属性变化的百分比
            turns (int): 效果持续的回合数
            effect_type: 效果类型标识，用于检查重复效果
        """
        self.name = name
        self.target = target
        self.stat = stat
        self.amount = amount
        self.turns = self.max_turns = turns
        self.effect_type = effect_type
        self.difference = 0

    def activate(self):
        """
        激活状态效果。

        计算属性实际变化量，应用到目标，并将此状态添加到目标的状态列表中。

        副作用:
            - 改变目标的指定属性
            - 将此状态添加到目标的状态列表
            - 输出状态应用信息
        """
        self.difference = int(self.target.stats[self.stat] * self.amount)
        self.target.stats[self.stat] += self.difference
        self.target.buffs_and_debuffs.append(self)
        state = "增强" if self.amount > 0 else "削弱"
        console.print(f"{self.target.name} 的 {self.stat} 被 {state}了 {abs(self.amount*100):.0f}% ，持续 {self.turns} 回合", style="green")

    def restart(self):
        """
        重置状态持续时间。

        将回合数重置为初始值，用于刷新效果持续时间。
        """
        self.turns = self.max_turns

    def check_turns(self):
        """
        检查并更新状态持续时间。

        减少剩余回合数，如果持续时间结束则移除状态效果。

        副作用:
            - 减少状态剩余回合数
            - 可能移除状态效果
        """
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self):
        """
        移除状态效果。

        还原目标属性的变化，并从目标的状态列表中移除此状态。

        副作用:
            - 还原目标的属性值
            - 从目标的状态列表中移除此状态
            - 输出状态结束信息
        """
        self.target.stats[self.stat] -= self.difference
        self.target.buffs_and_debuffs.remove(self)
        console.print(f"[red]{self.name}[/red] 的效果已结束")


class PoisonEffect(BuffDebuff):
    """
    毒素效果类，每回合对目标造成伤害的状态效果。

    继承自BuffDebuff类，但不改变属性值，而是每回合直接造成生命值损失。
    可以表示中毒、燃烧等持续伤害效果。

    属性:
        damage (int): 每回合造成的伤害值
    """
    def __init__(self, name, target: "Battler", stat, damage_per_turn, turns, effect_type="poison"):
        """
        初始化毒素效果实例。

        设置效果的基本属性，包括每回合造成的伤害值。

        参数:
            name (str): 效果名称
            target (Battler): 效果目标
            stat (str): 受影响的属性（一般为"hp"）
            damage_per_turn (int): 每回合造成的伤害值（负值）
            turns (int): 效果持续的回合数
            effect_type (str): 效果类型标识，默认为"poison"
        """
        super().__init__(name, target, stat, 0, turns, effect_type)
        self.damage = damage_per_turn

    def activate(self):
        """
        激活毒素效果。

        将此状态添加到目标的状态列表中，并输出相关信息。

        副作用:
            - 将此状态添加到目标的状态列表
            - 输出状态应用信息
        """
        self.target.buffs_and_debuffs.append(self)
        console.print(f"{self.target.name} 中了 {self.name}，每回合损失 {abs(self.damage)} HP ，持续 {self.turns} 回合", style="purple")

    def check_turns(self):
        """
        检查并更新毒素效果，对目标造成伤害。

        每回合对目标造成指定伤害，如果目标生命值降至0则杀死目标。
        然后减少剩余回合数，如果持续时间结束则移除状态效果。

        副作用:
            - 减少目标的生命值
            - 可能改变目标的存活状态
            - 减少状态剩余回合数
            - 可能移除状态效果
        """
        console.print(f"{self.target.name} 因 {self.name} 受到 {abs(self.damage)} 点伤害", style="red")
        self.target.stats["hp"] += self.damage
        if self.target.stats["hp"] <= 0:
            self.target.alive = False
            console.print(f"{self.target.name} 被 {self.name} 杀死了")
        super().check_turns()