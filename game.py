import cmd
import textwrap
import sys
import os
import random

import combat, enemies, text, inventory, player, items

from test.clear_screen import clear_screen, enter_clear_screen
from test.save_system import save_game, get_save_list, delete_save, load_game

#### 标题屏幕 #####
def title_screen_selection():
    text.title_screen()
    option = input("> ")
    while option not in ["1", "2", "3"]:
        print("请输入有效命令")
        option = input("> ")
    if option == "1":
        clear_screen()
        play()
    elif option == "2":
        text.help_menu()
    elif option == "3":
        sys.exit()

##### 库存菜单 #####
def inventory_selections(player):
    option = input("> ")
    while option.lower() != "q":
        match option.lower():
            case "u":
                player.use_item(player.inventory.use_item())
            case "s":
                player.money += player.inventory.sell_item()
            case "d":
                player.inventory.drop_item()
            case "e":
                player.equip_item(player.inventory.equip_item())
            case _:
                pass
        enter_clear_screen()
        text.inventory_menu()
        option = input("> ")
    enter_clear_screen()

def handle_save_menu(player):
    """处理存档菜单逻辑，返回可能更新的玩家对象"""
    save_option = int(input("> "))
    match save_option:
        case 1:
            save_name = input("输入存档名 (留空使用默认名称): ").strip()
            save_name = save_name if save_name else None
            save_metadata = save_game(player, save_name)
            print(f"游戏已保存: {save_metadata['name']}")
        case 2:
            saves = get_save_list()
            if not saves:
                print("没有可用存档。")
                return player
            text.display_save_list(saves)
            save_index = int(input("> "))
            if 1 <= save_index <= len(saves):
                loaded_player = load_game(saves[save_index-1]["name"])
                if loaded_player:
                    print(f"游戏已加载: {loaded_player.name} (等级 {loaded_player.level})")
                    return loaded_player
        case 3:
            saves = get_save_list()
            if not saves:
                print("没有可删除的存档")
                return player
            text.display_save_list(saves)
            save_index = int(input("> "))
            if 1 <= save_index <= len(saves):
                if delete_save(saves[save_index-1]["name"]):
                    print("存档已删除")
    return player

##### 初始化函数#####
def play():
    # 玩家实例
    my_player = player.Player("Test Player")

    debug_add_test_items(my_player)

    while my_player.alive:
        text.play_menu()
        option = input("> ")
        match option:
            case "1":
                battle_enemies = combat.create_enemy_group(my_player.level)
                combat.combat(my_player, battle_enemies)
                enter_clear_screen()
            case "2":
                clear_screen()
                text.show_stats(my_player)
                enter_clear_screen()
            case "3":
                clear_screen()
                my_player.assign_aptitude_points()
                enter_clear_screen()
            case "4":
                clear_screen()
                text.inventory_menu()
                my_player.inventory.show_inventory()
                inventory_selections(my_player)
            case "5":
                combat.fully_heal(my_player)
            case "6":
                clear_screen()
                text.save_load_menu()
                handle_save_menu(my_player)
                enter_clear_screen()
            case "7":
                clear_screen()
                my_player.add_exp(99999)
                enter_clear_screen()
            case "8":
                clear_screen()
                text.show_equipment_info(my_player)
                enter_clear_screen()
            case _:
                clear_screen()
                print("请输入有效命令")

def debug_add_test_items(my_player):
    # 添加一些测试项目
    items.hp_potions.add_to_inventory(my_player.inventory)
    items.mp_potions.add_to_inventory(my_player.inventory)
    items.long_sword.add_to_inventory(my_player.inventory)
    items.dagger.add_to_inventory(my_player.inventory)
    items.staff.add_to_inventory(my_player.inventory)
    items.cloth_armor.add_to_inventory(my_player.inventory)
    items.war_hammer.add_to_inventory(my_player.inventory)
    items.iron_armor.add_to_inventory(my_player.inventory)
    items.wooden_shield.add_to_inventory(my_player.inventory)
    items.straw_hat.add_to_inventory(my_player.inventory)
    items.gloves_wraps.add_to_inventory(my_player.inventory)
    items.footrags.add_to_inventory(my_player.inventory)

if __name__ == "__main__":
    title_screen_selection()