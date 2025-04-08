import cmd
import textwrap
import sys
import os
import random
import combat, enemies, text, inventory, player, items
from test.clear_screen import clear_screen, enter_clear_screen

from save_system import save_game, get_save_list, delete_save, load_game

def title_screen_selection():
    text.title_screen()
    option = int(input("> "))
    if option == 1:
        clear_screen()
        play()
    elif option == 2:
        text.help_menu()
    elif option == 3:
        sys.exit()
    while option not in [1,2,3]:
        print("请输入有效字符")
        option = int(input("> "))

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

##### 初始化函数#####
def play():
    my_player = player.Player("Test Player")

    items.hp_potions.add_to_inventory(my_player.inventory)
    items.mp_potions.add_to_inventory(my_player.inventory)
    items.long_sword.add_to_inventory(my_player.inventory)
    items.dagger.add_to_inventory(my_player.inventory)
    items.staff.add_to_inventory(my_player.inventory)
    items.cloth_armor.add_to_inventory(my_player.inventory)
    items.war_hammer.add_to_inventory(my_player.inventory)
    items.iron_armor.add_to_inventory(my_player.inventory)

    while my_player.alive:
        text.play_menu()
        option = int(input("> "))
        match option:
            case 1:
                enemy1 = enemies.Imp()
                enemy2 = enemies.Golem()
                battle_enemies = [enemy1, enemy2]
                combat.combat(my_player, battle_enemies)
                enter_clear_screen()
            case 2:
                clear_screen()
                text.show_stats(my_player)
                enter_clear_screen()
            case 3:
                clear_screen()
                my_player.assign_aptitude_points()
                enter_clear_screen()
            case 6:  # 新增存档/读档选项
                clear_screen()
                text.save_load_menu()
                save_option = int(input("> "))
                if save_option == 1:  # 保存游戏
                    save_name = input("输入存档名 (留空使用默认名称): ")
                    if not save_name.strip():
                        save_name = None
                    save_metadata = save_game(my_player, save_name)
                    print(f"游戏已保存: {save_metadata['name']}")
                elif save_option == 2:  # 加载游戏
                    saves = get_save_list()
                    text.display_save_list(saves)
                    save_index = int(input("> "))
                    if save_index > 0 and save_index <= len(saves):
                        loaded_player = load_game(saves[save_index-1]['name'])
                        if loaded_player:
                            my_player = loaded_player
                            print(f"游戏已加载: {loaded_player.name} (等级 {loaded_player.level})")
                elif save_option == 3:  # 删除存档
                    saves = get_save_list()
                    text.display_save_list(saves)
                    save_index = int(input("> "))
                    if save_index > 0 and save_index <= len(saves):
                        if delete_save(saves[save_index-1]['name']):
                            print("存档已删除")
                enter_clear_screen()
            case _:
                pass

if __name__ == "__main__":
    title_screen_selection()