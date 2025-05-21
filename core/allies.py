"""
盟友模块，定义可被召唤的友方战斗单位。

该模块实现了游戏中可作为玩家盟友的各种召唤生物，
这些生物具有预设的属性和能力，可以在战斗中辅助玩家。
所有盟友类型都继承自基础战斗单位类，但被标记为友方单位。
"""

import sys
sys.path.append("..")
from core import battler

class Summoned_skeleton(battler.Battler):
    """
    召唤骷髅类，一种基础召唤物盟友。

    实现了一个偏向于物理攻击的召唤生物，具有中等生命值、较高的物理攻击力
    但魔法能力较弱。作为玩家的盟友，能在战斗中提供额外的输出能力。

    属性:
        is_ally (bool): 标记该单位为友方单位，值为True
        stats (dict): 包含所有战斗属性的字典，继承自Battler类
    """
    def __init__(self) -> None:
        """
        初始化召唤骷髅实例。

        创建一个新的召唤骷髅对象，设置其初始战斗属性并将其标记为友方单位。
        """
        stats = {
            "max_hp": 370,
            "hp": 370,
            "mp": 30,
            "max_mp": 30,
            "atk": 17,
            "def": 7,
            "mat": 3,
            "mdf": 5,
            "agi": 10,
            "luk": 10,
            "crit": 5
        }
        super().__init__("小骨", stats)
        self.is_ally = True

class Summoned_fire_spirit(battler.Battler):
    """
    召唤火精灵类，一种高级召唤物盟友。

    实现了一个偏向于魔法攻击的召唤生物，具有较高生命值、出色的魔法攻击力
    和魔法防御力。作为玩家的高级盟友，能在战斗中提供强大的魔法输出支持。

    属性:
        is_ally (bool): 标记该单位为友方单位，值为True
        stats (dict): 包含所有战斗属性的字典，继承自Battler类
    """
    def __init__(self) -> None:
        """
        初始化召唤火精灵实例。

        创建一个新的召唤火精灵对象，设置其初始战斗属性并将其标记为友方单位。
        """
        stats = {
            "max_hp": 510,
            "hp": 510,
            "mp": 70,
            "max_mp": 70,
            "atk": 15,
            "def": 8,
            "mat": 22,
            "mdf": 17,
            "agi": 15,
            "luk": 15,
            "crit": 5
        }
        super().__init__("火精灵", stats)
        self.is_ally = True
