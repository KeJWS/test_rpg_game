from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.battler import Battler

from rich.console import Console

console = Console()

class Skill:
    """
    技能基类，所有技能类型的基础。

    定义了所有技能共有的基本属性，作为其他专用技能类的父类。

    属性:
        name (str): 技能名称
        description (str): 技能描述
        cost (int): 使用技能的消耗
        is_targeted (bool): 是否需要选择目标
        default_target (str): 未指定目标时的默认目标类型
    """
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        """
        初始化技能实例。

        设置技能的基本属性。

        参数:
            name (str): 技能名称
            description (str): 技能描述
            cost (int): 使用技能的消耗
            is_targeted (bool): 是否需要选择目标
            default_target (str): 未指定目标时的默认目标类型
        """
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target


class Spell(Skill):
    """
    法术类，消耗魔法值的技能。

    继承自Skill基类，表示消耗MP的法术技能，添加了基础威力属性
    和检查MP消耗的功能。

    属性:
        power (int): 法术的基础威力值
    """
    def __init__(self, name: str, description: str, power: int, cost: int, is_targeted: bool, default_target: str):
        """
        初始化法术实例。

        设置法术的基本属性，包括继承自基类的属性和法术特有的威力属性。

        参数:
            name (str): 法术名称
            description (str): 法术描述
            power (int): 法术基础威力
            cost (int): 魔法值消耗
            is_targeted (bool): 是否需要选择目标
            default_target (str): 默认目标类型
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.power = power

    def check_mp(self, caster: "Battler") -> bool:
        """
        检查施法者是否有足够的MP释放法术。

        如果MP足够，消耗相应数量并返回True；
        否则显示错误信息并返回False。

        参数:
            caster (Battler): 施法者

        返回:
            bool: 如果MP足够并成功消耗返回True，否则返回False

        副作用:
            - 减少施法者的MP
            - 输出释放法术的信息
        """

        if caster.stats["mp"] < self.cost:
            console.print("没有足够的 MP 释放技能", style="red")
            return False
        console.print(f"{caster.name} 释放了 {self.name}!", style="blue")
        caster.stats["mp"] -= self.cost
        return True


class Combo(Skill):
    """
    连招类，消耗连击点数的技能。

    继承自Skill基类，表示消耗连击点数(CP)的连招技能，
    提供了检查和消耗CP的功能。
    """
    def check_cp(self, caster: "Battler") -> bool:
        """
        检查施法者是否有足够的连击点数使用连招。

        如果CP足够，消耗相应数量并返回True；
        否则显示错误信息并返回False。

        参数:
            caster (Battler): 使用连招的战斗单位

        返回:
            bool: 如果CP足够并成功消耗返回True，否则返回False

        副作用:
            - 减少施法者的连击点数
            - 输出使用连招的信息
        """

        if caster.combo_points < self.cost:
            console.print("没有足够的 CP 释放技能", style="red")
            return False
        console.print(f"{caster.name} 使用了 {self.name}!", style="yellow")
        caster.combo_points -= self.cost
        return True