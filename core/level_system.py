"""
等级系统模块，处理角色的经验、等级和属性成长。

该模块实现了游戏中的等级提升系统，包括经验值计算、等级提升判定和不同职业的属性成长设置。
作为角色成长的核心机制，提供了随游戏进程提升角色能力的功能。
"""

from data import EXPERIENCE_RATE
from rich.console import Console

console = Console()

class LevelSystem:
    """
    等级系统类，管理角色的等级、经验和属性成长。

    实现游戏中角色的升级机制，包括经验值累积、等级提升和基于职业的属性成长。
    提供了计算升级所需经验、获取经验值和处理等级提升的方法。

    属性:
        level (int): 当前等级
        xp (int): 当前经验值
        class_name (str): 职业名称，决定属性成长方向
        aptitude_points (int): 可用于自定义提升属性的点数
        xp_to_next_level (int): 升至下一级所需的经验值
    """
    def __init__(self, level=1, xp=0, class_name=""):
        """
        初始化等级系统实例。

        创建一个新的等级系统对象，设置初始等级、经验值和职业。

        参数:
            level (int, optional): 初始等级，默认为1
            xp (int, optional): 初始经验值，默认为0
            class_name (str, optional): 职业名称，默认为空字符串
        """
        self.level = level
        self.xp = xp
        self.class_name = class_name
        self.aptitude_points = 0
        self.xp_to_next_level = self.exp_required_formula()

    def exp_required_formula(self):
        """
        计算升级所需的经验值。

        根据当前等级计算升至下一级所需的经验值，使用非线性公式确保
        随着等级提高所需经验值增长更快。

        返回:
            int: 升至下一级所需的经验值
        """
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def gain_exp(self, battler, amount):
        """
        获取经验值并检查是否升级。

        将指定量的经验值添加到当前经验值，并考虑战斗单位的幸运属性和全局经验率。
        然后检查是否满足升级条件。

        参数:
            battler: 获得经验的战斗单位对象
            amount (int): 基础经验值数量

        副作用:
            - 增加当前经验值
            - 可能触发等级提升
            - 在控制台显示获得的经验值
        """
        earned = (amount + battler.stats["luk"]) * EXPERIENCE_RATE
        self.xp += earned
        console.print(f"获得了 {earned}xp")
        self.check_level_up(battler)

    def check_level_up(self, battler):
        """
        检查并处理多次升级。

        检查当前经验值是否足够升级，如果是则进行升级并重新计算下一级所需经验值。
        支持一次获得足够经验值连升多级的情况。

        参数:
            battler: 需要检查升级的战斗单位对象

        副作用:
            可能触发一次或多次等级提升
        """
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self.exp_required_formula()
            self.level_up(battler)

    def level_up(self, battler):
        """
        处理角色升级效果。

        执行升级时的属性提升，包括基础属性增长、增加能力点，
        应用职业特定成长，并恢复生命值和魔法值。

        参数:
            battler: 进行升级的战斗单位对象

        副作用:
            - 增加能力点
            - 提升所有基础属性值
            - 应用职业特定的属性成长
            - 恢复战斗单位的生命值和魔法值
            - 在控制台显示升级信息
        """
        console.print(f"升级! 现在的等级是: {self.level}, 有 {self.aptitude_points + 1} 个能力点", style="bold yellow")
        self.aptitude_points += 1

        for stat in battler.stats:
            battler.stats[stat] += 1
        battler.stats["crit"] -= 1
        battler.stats["anti_crit"] -= 1
        battler.stats["max_hp"] += 4
        battler.stats["max_mp"] += 2

        self.apply_class_growth(battler)
        battler.recover_mp(9999)
        battler.heal(9999)

    def apply_class_growth(self, battler):
        """
        应用职业特定的属性成长。

        根据角色的职业类型应用不同的属性成长方案，每个职业有独特的属性加成模式。

        参数:
            battler: 需要应用职业成长的战斗单位对象

        副作用:
            - 根据职业特性修改战斗单位的各项属性
            - 在控制台显示属性变化信息

        注意:
            如果角色的职业名称不在预定义的成长列表中，则不会应用任何特殊成长
        """
        growth = {
            "战士": {"atk": 2, "max_hp": 5},
            "盗贼": {"agi": 2, "crit": 1},
            "法师": {"mat": 2, "max_mp": 5},
            "弓箭手": {"atk": 2, "crit": 1},
            "圣骑士": {"atk": 2, "mat": 1, "max_hp": 10, "agi": -1},
            "死灵法师": {"mat": 3, "max_mp": 10, "max_hp": -15},
        }
        for stat, val in growth.get(self.class_name, {}).items():
            battler.stats[stat] += val
            console.print(f"{stat} {'+' if val > 0 else ''}{val}", style="green" if val > 0 else "red")
