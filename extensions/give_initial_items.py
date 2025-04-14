import sys
sys.path.append("..")
import items
from test.clear_screen import enter_clear_screen
import test.fx as fx

def give_initial_items(my_player):
    option = str(input("> "))
    while option not in ["1", "2", "3", "4"]:
        option = str(input("> "))

    items.mp_potion.add_to_inventory_player(my_player.inventory)
    items.hp_potion.add_to_inventory_player(my_player.inventory)
    my_player.add_money(100)

    if option == "1":
        items.rusty_sword.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
        items.atk_gems.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "战士"
    elif option == "2":
        items.broken_dagger.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
        items.agi_gems.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "盗贼"
    elif option == "3":
        items.old_staff.add_to_inventory_player(my_player.inventory)
        items.old_robes.add_to_inventory_player(my_player.inventory)
        items.grimoire_fireball.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "法师"
    elif option == "4":
        items.wood_bow.add_to_inventory_player(my_player.inventory)
        items.leather_armor.add_to_inventory_player(my_player.inventory)
        items.crit_gems.add_to_inventory_player(my_player.inventory)
        my_player.class_name = "弓箭手"

    enter_clear_screen()
    print(f"\n你选择了 {my_player.class_name} 职业")

def apply_class_bonuses(my_player):
    """根据职业给予初始属性加成"""
    class_bonuses = {
        "战士": {"max_hp": 50, "atk": 3, "def": 2},
        "盗贼": {"agi": 5, "crit": 1, "luk": 3},
        "法师": {"max_mp": 30, "mat": 5, "mdf": 2},
        "弓箭手": {"atk": 3, "agi": 1, "crit": 2},
    }

    if my_player.class_name in class_bonuses:
        bonuses = class_bonuses[my_player.class_name]
        for stat, value in bonuses.items():
            my_player.stats[stat] += value
            if value > 0:
                print(fx.cyan(f"{stat} +{value}"))
