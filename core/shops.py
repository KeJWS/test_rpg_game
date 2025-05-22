"""
商店系统模块，实现游戏中的商品交易功能。

该模块定义了商店类，允许玩家购买、出售物品，为游戏提供经济系统。
商店可以根据提供的物品集合随机生成库存，提供游戏中的商品交易场所。
"""

import random
import sys
sys.path.append("..")
import bag

class Shop():
    """
    商店类，管理游戏中的商品交易系统。

    处理商店的库存管理和商品生成，从指定的物品集合中随机选择物品
    添加到商店库存中，支持玩家与商店之间的物品交易。

    属性:
        item_set (list): 可能出现在商店中的物品集合
        inventory (Inventory): 存储商店当前库存的对象
    """
    def __init__(self, item_set) -> None:
        """
        初始化商店实例。

        创建一个新的商店对象，设置其可售卖的物品集合，
        初始化商店的库存系统，并随机生成初始商品。

        参数:
            item_set (list): 可售卖物品的集合，商店将从中随机选择物品
        """
        self.item_set = item_set
        self.inventory = bag.Inventory()
        self.add_items_to_inventory_shop()

    def add_items_to_inventory_shop(self):
        """
        将随机物品添加到商店的库存中。

        从商店的物品集合中随机选择一定数量的物品，为每个物品创建新实例，
        如果物品支持品质重设，则可能重新设置物品品质，最后将物品添加到商店库存。

        副作用:
            - 向商店库存添加随机数量的物品
            - 可能修改添加物品的品质属性
        """
        item_quantity = random.randint(len(self.item_set)//2, len(self.item_set))
        for _ in range(item_quantity):
            base_item = random.choice(self.item_set)
            new_item = base_item.clone(1)
            if hasattr(new_item, "reroll_quality"):
                new_item.reroll_quality()
            new_item.add_to_inventory(self.inventory, 1)