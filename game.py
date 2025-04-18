import sys
import random

import combat, text, player, items, events, map
from test.clear_screen import enter_clear_screen, clear_screen
import test.fx
import data.event_text

from inventory import Inventory_interface as interface

from tools import dev_tools
from tools import command_parser as cp


# *标题菜单*
def title_screen_selections():
    text.title_screen()
    while (option := input("> ")) not in {"1", "2", "3"}:
        print("请输入有效命令")
    match option:
        case "1": clear_screen(); play()
        case "2": text.help_menu()
        case "3":sys.exit()


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


# *主游戏循环*
def play(p=None):
    from extensions.give_initial_items import give_initial_items, apply_class_bonuses
    if p is None:
        p = player.Player("Test Player")
        print(data.event_text.initial_event_text)
        give_initial_items(p)
        print(test.fx.red("\n[ 记得在库存 > 装备物品中装备这些物品 ]"))
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
            case "hdc":
                clear_screen()
                command = input("> ")
                dev_tools.handle_debug_command(command, p.inventory)
                enter_clear_screen()
            case _: clear_screen(); print("请输入有效命令")

    choice = input("是否要转生? (y/n): ")
    if choice.lower() == "y":
        p.rebirth(map.world_map)
        enter_clear_screen()
        play(p)

if __name__ == "__main__":
    title_screen_selections()
