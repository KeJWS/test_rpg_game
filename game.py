"""
主游戏模块，包含游戏的入口点和主循环。

该模块定义了游戏的主要流程控制，包括标题菜单、游戏循环、背包管理和存档加载等核心功能。
作为游戏的主要控制中心，协调各个子系统的交互和状态管理。
"""

import sys
from rich.console import Console

import player
import ui.text as text
import tools.save_system as sl
import data.event_text

from world import map
from test.clear_screen import enter_clear_screen, clear_screen
from inventory import Inventory_interface as interface
from tools import command_parser as cp

console = Console()


# *标题菜单*
def title_screen_selections():
    """
    显示标题菜单并处理用户选择。

    展示游戏标题屏幕并处理用户的选择，包括开始游戏、查看帮助或退出游戏。
    会持续等待直到用户提供有效输入。
    """
    text.title_screen()
    while (option := input("> ")) not in {"1", "2", "3"}:
        print("请输入有效命令")
    match option:
        case "1": clear_screen(); play()
        case "2": text.help_menu(); enter_clear_screen()
        case "3": enter_clear_screen(); sys.exit()


# *背包菜单*
def inventory_selections(player):
    """
    处理背包菜单的用户选择。

    提供背包操作界面，允许玩家使用、丢弃、装备物品或比较装备。
    会持续接收输入直到用户选择退出(q)。

    参数:
        player: 玩家对象，包含背包属性
    """
    while (option := input("> ").lower()) != "q":
        match option:
            case "u": clear_screen(); interface(player.inventory).use_item().activate(player)
            case "d": clear_screen(); interface(player.inventory).drop_item()
            case "e": clear_screen(); player.equip_item(interface(player.inventory).equip_item())
            case "c": clear_screen(); interface(player.inventory).compare_equipment()
        enter_clear_screen()
        text.inventory_menu()


# *存档相关*
def save_load_game(player):
    """
    处理游戏存档和加载功能。

    提供游戏存档和加载界面，允许玩家保存当前游戏进度或加载之前的存档。
    注意：该功能仅在DEBUG模式下可用。

    参数:
        player: 当前玩家对象，用于保存或被加载的存档替代

    返回:
        player: 可能是原始玩家对象或从存档加载的新玩家对象
    """
    from data.constants import DEBUG
    if not DEBUG:
        return
    text.save_load_menu()
    save_option = input("> ").lower()
    if save_option == "s":
        save_name = input("输入存档名 (留空使用默认名称): ")
        if not save_name.strip():
            save_name = None
        player.unequip_all()
        save_metadata = sl.save_game(player, save_name)
        print(f"游戏已保存: {save_metadata['name']}")
        return player
    elif save_option == "l":
        saves = sl.get_save_list()
        text.display_save_list(saves)
        save_index = int(input("> "))
        if save_index > 0 and save_index <= len(saves):
            loaded_player = sl.load_game(saves[save_index-1]['name'])
            if loaded_player:
                print(f"游戏已加载: {loaded_player.name} (等级: {loaded_player.ls.level}, 职业: {loaded_player.ls.class_name})")
                return loaded_player


# *主游戏循环*
def play(p=None):
    """
    启动主游戏流程。

    初始化游戏环境并开始主游戏循环。如果没有提供玩家对象，
    将创建一个新角色并分配初始物品和职业加成，然后进入游戏循环。

    参数:
        p: 可选的玩家对象，用于继续游戏或从存档加载。默认为None，表示创建新角色。
    """
    from extensions.give_initial_items import give_initial_items, apply_class_bonuses
    if p is None:
        p = player.Player("Test Player")
        console.print(data.event_text.initial_event_text())
        give_initial_items(p)
        console.print("\n[ 记得在库存 > 装备物品中装备这些物品 ]", style="bold red")
    print()
    apply_class_bonuses(p)
    enter_clear_screen()
    game_loop(p)

def game_loop(p):
    """
    游戏主循环，处理玩家在游戏世界中的各种交互。

    提供主游戏界面，让玩家可以在地图上移动、查看属性、分配能力点、
    访问背包、查看地图、查看任务或保存/加载游戏。当玩家死亡时，
    提供转生选项以继续游戏。

    参数:
        p: 玩家对象，包含玩家的所有状态和属性
    """
    map.world_map.get_current_region_info()
    enter_clear_screen()
    event_chances = (60, 25, 15) # 战斗、商店、治疗的概率
    while p.alive:
        text.play_menu()
        match cp.handle_command(input("> "), p):
            case "w": clear_screen(); map.world_map.generate_random_event(p, *event_chances); p.decrease_hunger(1); enter_clear_screen()
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
