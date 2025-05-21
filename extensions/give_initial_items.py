"""
初始物品分配模块，负责玩家角色创建时的装备与物品发放。

该模块实现了根据玩家选择的职业类型，为新创建的角色分配初始装备、
物品和属性加成的功能。每种职业都有特定的起始装备和属性特性，
确保游戏开始时角色具有合适的基础能力。
"""

import random
import sys
sys.path.append("..")
import items
import ui.fx as fx
from ui.clear_screen import enter_clear_screen

def give_initial_items(my_player):
    """
    根据玩家选择分配初始物品和设置职业。

    接收玩家输入的职业选择，根据选择为玩家分配相应的初始装备、
    物品和金钱，并设置职业类型。所有玩家都会获得基础物品
    （如生命药水、魔法药水和面包），然后根据职业获得专属装备。

    参数:
        my_player: 玩家对象，用于接收物品和设置职业

    副作用:
        - 向玩家库存添加物品
        - 增加玩家金钱
        - 设置玩家职业
        - 显示职业选择结果
    """
    option = str(input("> "))
    while option not in ["1", "2", "3", "4", "5", "6", ""]:
        option = str(input("> "))

    my_player.add_money(120)
    items.mp_potion.add_to_inventory_player(my_player.inventory)
    items.hp_potion.add_to_inventory_player(my_player.inventory)

    items.bread.add_to_inventory_player(my_player.inventory)

    if option == "1":
        default_selection_warrior(my_player)
    elif option == "2":
        items.basic_equipments[random.choice(["training_dagger", "broken_dagger"])].add_to_inventory_player(my_player.inventory)
        items.basic_equipments["padded_vest"].add_to_inventory_player(my_player.inventory)
        items.jewel_data["agi_gems"].add_to_inventory_player(my_player.inventory)
        my_player.add_money(50)
        my_player.ls.class_name = "盗贼"
    elif option == "3":
        items.equipment_data["fire_staff"].add_to_inventory_player(my_player.inventory)
        items.basic_equipments[random.choice(["old_robes", "padded_vest"])].add_to_inventory_player(my_player.inventory)
        my_player.ls.class_name = "法师"
    elif option == "4":
        items.basic_equipments[random.choice(["wood_bow", "self_bow"])].add_to_inventory_player(my_player.inventory)
        items.equipment_data["leather_armor"].add_to_inventory_player(my_player.inventory)
        items.jewel_data["crit_gems"].add_to_inventory_player(my_player.inventory)
        my_player.ls.class_name = "弓箭手"
    elif option == "5":
        items.equipment_data[random.choice(["rusty_sword", "long_sword"])].add_to_inventory_player(my_player.inventory)
        items.basic_equipments[random.choice(["novice_armor", "padded_vest"])].add_to_inventory_player(my_player.inventory)
        items.equipment_data["wooden_shield"].add_to_inventory_player(my_player.inventory)
        items.grimoires[1].add_to_inventory_player(my_player.inventory)
        my_player.ls.class_name = "圣骑士"
    elif option == "6":
        items.basic_equipments[random.choice(["old_staff", "beginner_wand"])].add_to_inventory_player(my_player.inventory)
        items.basic_equipments[random.choice(["old_robes", "padded_vest"])].add_to_inventory_player(my_player.inventory)
        items.grimoires[4].add_to_inventory_player(my_player.inventory)
        my_player.ls.class_name = "死灵法师"
    else:
        default_selection_warrior(my_player)

    enter_clear_screen()
    print(f"\n你选择了 {my_player.ls.class_name} 职业")

def apply_class_bonuses(my_player):
    """
    根据玩家职业应用相应的属性加成。

    检查玩家当前职业，从预定义的职业属性加成配置中获取对应的属性修正值，
    并应用到玩家角色身上。不同职业有各自的特色属性成长方向。

    参数:
        my_player: 要应用属性加成的玩家对象

    副作用:
        - 修改玩家的属性值
        - 在控制台显示属性变化
        - 恢复玩家的生命值和魔法值
    """
    class_bonuses = {
        "战士": {"max_hp": 50, "atk": 3, "def": 3},
        "盗贼": {"agi": 5, "crit": 1, "luk": 3},
        "法师": {"max_mp": 25, "mat": 5, "mdf": 2},
        "弓箭手": {"atk": 3, "agi": 1, "crit": 2},
        "圣骑士": {"atk": 5, "def": 3, "mat": 5, "agi": -3},
        "死灵法师": {"max_mp": 60, "mat": 7, "def": -5, "max_hp": -90},
    }

    if my_player.ls.class_name in class_bonuses:
        bonuses = class_bonuses[my_player.ls.class_name]
        for stat, value in bonuses.items():
            my_player.stats[stat] += value
            if value > 0:
                print(fx.cyan(f"{stat} +{value}"))
            else:
                print(fx.red(f"{stat} -{abs(value)}"))
        my_player.recover_mp(9999); my_player.heal(9999)

def default_selection_warrior(my_player):
    """
    为玩家分配战士职业的默认初始装备。

    当玩家没有明确选择职业或选择了战士职业时使用此函数，
    为玩家添加战士职业的基本武器、护甲和宝石，并设置职业为"战士"。

    参数:
        my_player: 要设置为战士职业的玩家对象

    副作用:
        - 向玩家库存添加武器（随机选择生锈的剑或木棒）
        - 向玩家库存添加护甲（随机选择新手护甲或棉背心）
        - 向玩家库存添加攻击宝石
        - 设置玩家职业为战士
    """
    items.basic_equipments[random.choice(["rusty_sword", "wooden_club"])].add_to_inventory_player(my_player.inventory)
    items.basic_equipments[random.choice(["novice_armor", "padded_vest"])].add_to_inventory_player(my_player.inventory)
    items.jewel_data["atk_gems"].add_to_inventory_player(my_player.inventory)
    my_player.ls.class_name = "战士"
