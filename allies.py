import combat
# 导入战斗以继承战者的数据

'''
盟友在战斗中帮助玩家。目前，这里详述的所有盟友都是通过法术召唤的，
但也可以在此处定义由事件或任何其他原因授予的盟友。
主要有他们的统计数据。
'''

class Summoned_skeleton(combat.Battler):
    def __init__(self) -> None:
        stats = {
            "max_hp": 370,
            "hp": 370,
            "mp": 30,
            "max_mp": 30,
            "atk": 17,
            "def": 10,
            "mat": 3,
            "mdf": 5,
            "agi": 10,
            "luk": 10,
            "crit": 5
        }
        super().__init__("小骨", stats)
        self.is_ally = True

class Summoned_fire_spirit(combat.Battler):
    def __init__(self) -> None:
        stats = {
            "max_hp": 550,
            "hp": 550,
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
