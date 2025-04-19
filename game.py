import sys

import text, player, map
from test.clear_screen import enter_clear_screen, clear_screen
from tools.save_system import save_game, get_save_list, load_game
import test.fx
import data.event_text

from data.constants import DEBUG
from inventory import Inventory_interface as interface
from tools import command_parser as cp


# *标题菜单*
def title_screen_selections():
    text.title_screen()
    while (option := input("> ")) not in {"1", "2", "3"}:
        print("请输入有效命令")
    match option:
        case "1": clear_screen(); play()
        case "2": text.help_menu(); enter_clear_screen()
        case "3": enter_clear_screen(); sys.exit()


# *背包菜单*
def inventory_selections(player):
    while (option := input("> ").lower()) != "q":
        match option:
            case "u": clear_screen(); player.use_item(interface(player.inventory).use_item())
            case "d": clear_screen(); interface(player.inventory).drop_item()
            case "e": clear_screen(); player.equip_item(interface(player.inventory).equip_item())
            case "c": clear_screen(); interface(player.inventory).compare_equipment()
        enter_clear_screen()
        text.inventory_menu()


def save_load_game(player):
    if not DEBUG:
        return
    text.save_load_menu()
    save_option = input("> ").lower()
    if save_option == "s":
        save_name = input("输入存档名 (留空使用默认名称): ")
        if not save_name.strip():
            save_name = None
        player.unequip_all()
        save_metadata = save_game(player, save_name)
        print(f"游戏已保存: {save_metadata['name']}")
        return player
    elif save_option == "l":
        saves = get_save_list()
        text.display_save_list(saves)
        save_index = int(input("> "))
        if save_index > 0 and save_index <= len(saves):
            loaded_player = load_game(saves[save_index-1]['name'])
            if loaded_player:
                print(f"游戏已加载: {loaded_player.name} (等级: {loaded_player.level}, 职业: {loaded_player.class_name})")
                return loaded_player


# *主游戏循环*
def play(p=None):
    from extensions.give_initial_items import give_initial_items, apply_class_bonuses
    if p is None:
        p = player.Player("Test Player")
        print(data.event_text.initial_event_text)
        give_initial_items(p)
        print(test.fx.yellow("\n[ 记得在库存 > 装备物品中装备这些物品 ]"))
    print()
    apply_class_bonuses(p)
    enter_clear_screen()
    game_loop(p)

def game_loop(p):
    print(map.world_map.get_current_region_info())
    enter_clear_screen()
    event_chances = (65, 20, 15)  # 战斗、商店、治疗的概率
    while p.alive:
        text.play_menu()
        match cp.handle_command(input("> "), p):
            case "w": clear_screen(); map.world_map.generate_random_event(p, *event_chances); enter_clear_screen()
            case "s": clear_screen(); text.show_stats(p); enter_clear_screen()
            case "a": clear_screen(); p.assign_aptitude_points(); enter_clear_screen()
            case "i": clear_screen(); text.inventory_menu(); interface(p.inventory).show_inventory(); inventory_selections(p)
            case "m": clear_screen(); text.map_menu(p); enter_clear_screen()
            case "q": clear_screen(); text.show_all_quests(p); enter_clear_screen()
            case "sl": clear_screen(); p = save_load_game(p); enter_clear_screen()
            case _: clear_screen(); print("请输入有效命令")

    choice = input("是否要转生? (y/n): ")
    if choice.lower() == "y":
        p.rebirth(map.world_map)
        enter_clear_screen()
        play(p)

if __name__ == "__main__":
    title_screen_selections()
