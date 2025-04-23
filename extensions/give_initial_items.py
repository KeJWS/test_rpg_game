import sys
sys.path.append("..")
import items
import test.fx as fx
from test.clear_screen import enter_clear_screen

def give_initial_items(my_player):
    option = str(input("> "))
    while option not in ["1", "2", "3", "4", "5", "6", ""]:
        option = str(input("> "))

    my_player.add_money(120)
    items.mp_potion.add_to_inventory_player(my_player.inventory)
    items.hp_potion.add_to_inventory_player(my_player.inventory)

    if option == "1":
        default_selection_warrior(my_player)
    elif option == "2":
        items.basic_equipments["broken_dagger"].add_to_inventory_player(my_player.inventory)
        items.basic_equipments["novice_armor"].add_to_inventory_player(my_player.inventory)
        items.agi_gems.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "盗贼"
    elif option == "3":
        items.basic_equipments["old_staff"].add_to_inventory_player(my_player.inventory)
        items.basic_equipments["old_robes"].add_to_inventory_player(my_player.inventory)
        items.grimoires[0].add_to_inventory_player(my_player.inventory)
        my_player.class_name = "法师"
    elif option == "4":
        items.basic_equipments["wood_bow"].add_to_inventory_player(my_player.inventory)
        items.equipment_data["leather_armor"].add_to_inventory_player(my_player.inventory)
        items.crit_gems.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "弓箭手"
    elif option == "5":
        items.basic_equipments["rusty_sword"].add_to_inventory_player(my_player.inventory)
        items.basic_equipments["novice_armor"].add_to_inventory_player(my_player.inventory)
        items.equipment_data["wooden_shield"].add_to_inventory_player(my_player.inventory)
        items.grimoires[1].add_to_inventory_player(my_player.inventory)
        my_player.class_name = "圣骑士"
    elif option == "6":
        items.basic_equipments["old_staff"].add_to_inventory_player(my_player.inventory)
        items.basic_equipments["old_robes"].add_to_inventory_player(my_player.inventory)
        items.grimoires[4].add_to_inventory_player(my_player.inventory)
        my_player.class_name = "死灵法师"
    else:
        default_selection_warrior(my_player)

    enter_clear_screen()
    print(f"\n你选择了 {my_player.class_name} 职业")

def apply_class_bonuses(my_player):
    """根据职业给予初始属性加成"""
    class_bonuses = {
        "战士": {"max_hp": 50, "atk": 3, "def": 3},
        "盗贼": {"agi": 5, "crit": 1, "luk": 3},
        "法师": {"max_mp": 25, "mat": 5, "mdf": 2},
        "弓箭手": {"atk": 3, "agi": 1, "crit": 2},
        "圣骑士": {"atk": 5, "def": 3, "mat": 5, "agi": -3},
        "死灵法师": {"max_mp": 60, "mat": 7, "def": -5, "max_hp": -70},
    }

    if my_player.class_name in class_bonuses:
        bonuses = class_bonuses[my_player.class_name]
        for stat, value in bonuses.items():
            my_player.stats[stat] += value
            if value > 0:
                print(fx.cyan(f"{stat} +{value}"))
            else:
                print(fx.red(f"{stat} -{abs(value)}"))
        my_player.recover_mp(9999); my_player.heal(9999)

def default_selection_warrior(my_player):
    items.basic_equipments["rusty_sword"].add_to_inventory_player(my_player.inventory)
    items.basic_equipments["novice_armor"].add_to_inventory_player(my_player.inventory)
    items.atk_gems.add_to_inventory_player(my_player.inventory)
    my_player.class_name = "战士"
