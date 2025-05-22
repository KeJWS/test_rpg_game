"""
命令解析模块，处理游戏中的用户输入命令。

该模块提供了一套命令解析系统，用于解析和执行玩家在游戏中输入的各类命令。
包括玩家状态查询、物品管理、商店交互以及开发调试等功能的命令处理。
"""

from data import DEBUG

from rich.console import Console

import events
import mods.debug_help
from ui import text
from core import shops
from mods import dev_tools as debug
from bag import InventoryInterface as interface
from enemies import ENEMY_DATA
from ui import clear_screen, enter_clear_screen, screen_wrapped

console = Console()

SHOP_DICT = {
    # "jack": events.shop_jack_weapon,
    # "anna": events.shop_anna_armor,
    # "rik": events.shop_rik_armor,
    # "itz": events.shop_itz_magic
}

@screen_wrapped
def show_help(topic=None):
    """
    显示指定主题的帮助信息。

    根据提供的主题参数显示对应的命令帮助文档。如果未指定主题或主题不存在，
    则显示默认的帮助信息。此函数由screen_wrapped装饰器包装，会自动处理屏幕清理。

    参数:
        topic: 要显示帮助信息的主题名称
    """
    command_docs = mods.debug_help.command_docs
    print(command_docs.get(topic, command_docs["default"]))

def handle_command(command: str, player):
    """
    处理用户输入的命令字符串。

    解析命令字符串，识别主命令和子命令，并根据命令类型调用相应的处理函数。
    支持玩家属性查询、物品管理、商店交互和战斗调试等命令。

    参数:
        command: 用户输入的命令字符串
        player: 当前玩家对象，命令操作的目标

    返回:
        str: 如果命令无法识别，返回原命令字符串，否则返回None
    """
    tokens = command.strip().split()
    if not tokens:
        show_help()
        return

    main = tokens[0]
    sub = None
    if "." in main:
        main, sub = main.split(".", 1)

    if main == "p":
        match sub:
            case None: handle_p_command(tokens, player)
            case "i": handle_pi_command(tokens, player)
            case "gold": player.add_money(int(tokens[1])) if tokens[1].isdigit() and DEBUG else None; enter_clear_screen()
            case "exp": player.add_exp(int(tokens[1])) if tokens[1].isdigit() and DEBUG else None; enter_clear_screen()
            case "ap": player.ls.aptitude_points += int(tokens[1]) if tokens[1].isdigit() and DEBUG else None; enter_clear_screen()
            case _: debug.debug_print(f"未知 p 命令模块: {main}"); enter_clear_screen(); return command

    elif main in SHOP_DICT and DEBUG:
        if sub == "i":
            handle_shop_command(main, SHOP_DICT[main], tokens, player)

    elif main == "a" and sub == "d":
        if len(tokens) >= 3 and tokens[1] == "-db":
            enemy_name = tokens[2]
            if enemy_name in ENEMY_DATA:
                enemy = ENEMY_DATA[enemy_name].clone()
                clear_screen()
                text.display_battle_stats(player, enemy)
                enter_clear_screen()
    else:
        if DEBUG:
            debug.debug_print(f"未知命令模块: {tokens[0]}")
            enter_clear_screen()
        return command

def handle_shop_command(shop_name, shop_data, tokens, player):
    """
    处理与商店相关的命令。

    创建指定商店实例并允许玩家与商店交互。
    当前主要处理购买物品的命令。

    参数:
        shop_name: 商店名称
        shop_data: 商店数据对象，包含物品集合
        tokens: 命令分割后的标记列表
    """
    if tokens[1] == "-buy":
        clear_screen()
        vendor = shops.Shop(shop_data.item_set)
        player.buy_from_vendor(vendor)

def handle_p_command(tokens, player):
    """
    处理玩家(p)命令。

    根据子命令执行不同的玩家相关操作，如显示属性、装备信息、治疗、
    恢复魔法值、切换自动战斗模式等。通过映射表实现命令与函数的对应。

    参数:
        tokens: 命令分割后的标记列表
    """
    subcommand_map = {
        "-hp": screen_wrapped(lambda: print(f"HP: {player.stats['hp']}/{player.stats['max_hp']}")),
        "-mp": screen_wrapped(lambda: print(f"MP: {player.stats['mp']}/{player.stats['max_mp']}")),
        "-gold": screen_wrapped(lambda: print(f"💰: {player.money}")),
        "-se": screen_wrapped(lambda: text.show_equipment_info(player)),
        "-sk": screen_wrapped(lambda: text.show_skills(player)),
        "-stats": screen_wrapped(lambda: text.debug_show_stats(player)),
        "-bag": lambda: (debug.handle_debug_command("bag", player.inventory), enter_clear_screen()),
        "-heal": screen_wrapped(lambda: player.heal(9999) if DEBUG else None),
        "-mana": screen_wrapped(lambda: player.recover_mp(9999) if DEBUG else None),
        "-level": screen_wrapped(lambda: handle_level_command(tokens, player)),
        "-auto": screen_wrapped(lambda: player.change_auto_mode() if DEBUG else None),
    }

    if len(tokens) == 1 or tokens[1] == "--help":
        show_help("p")
        return

    func = subcommand_map.get(tokens[1])
    if func:
        func()
    else:
        debug.debug_print(f"未知的 p 玩家指令: {tokens[1]}")
        show_help("p")

def handle_pi_command(tokens, player):
    """
    处理玩家物品(p.i)命令。

    处理与玩家背包和物品相关的各种操作，包括使用物品、丢弃物品、装备物品、
    比较装备、查看物品详情、整理背包等。通过映射表实现命令与功能的对应。

    参数:
        tokens: 命令分割后的标记列表
    """
    inv = player.inventory
    subcommand_map = {
        "-U": screen_wrapped(lambda: player.use_item(interface(inv).use_item())),
        "-D": screen_wrapped(lambda: interface(inv).drop_item()),
        "-E": screen_wrapped(lambda: player.equip_item(interface(inv).equip_item())),
        "-C": screen_wrapped(lambda: interface(inv).compare_equipment()),
        "-ua": screen_wrapped(lambda: player.unequip_all()),
        "-vi": screen_wrapped(lambda: print(interface(inv).view_item().get_detailed_info())),
        "-show": screen_wrapped(lambda: inv.show_inventory_item()),
        "--help": lambda: show_help("p.i"),
        "--give-all": lambda: (debug.handle_debug_command("give-all", inv), enter_clear_screen()),
        "-spawn": screen_wrapped(lambda: handle_spawn_item_command(tokens, player)),
        "-sort": screen_wrapped(lambda: inv.sort_items()),
        "-count": screen_wrapped(lambda: text.backpack_item_stats(inv)),
    }

    if len(tokens) == 1:
        clear_screen()
        inv.show_inventory_item()
        enter_clear_screen()
        return

    func = subcommand_map.get(tokens[1])
    if func:
        func()
    else:
        debug.debug_print(f"未知的 p.i 玩家指令: {tokens[1]}")
        show_help("p.i")

def handle_level_command(tokens, player):
    """
    处理玩家等级相关命令。

    在调试模式下允许直接修改玩家等级。通过为玩家添加足够的经验值
    使其升级到指定等级。仅在调试模式下可用。

    参数:
        tokens: 命令分割后的标记列表
    """
    if not DEBUG:
        return
    if len(tokens) > 2 and tokens[2].isdigit():
        target_level = int(tokens[2])
        current_level = player.ls.level
        if target_level > current_level:
            for _ in range(target_level - current_level):
                player.add_exp(player.ls.xp_to_next_level)

def handle_spawn_item_command(tokens, player):
    """
    处理生成物品命令。

    在调试模式下，根据指定的物品名称和数量在玩家背包中生成物品。
    如果未指定数量，默认生成1个。

    参数:
        tokens: 命令分割后的标记列表
    """
    if len(tokens) >= 3:
        item_name = tokens[2]
        quantity = int(tokens[3]) if len(tokens) > 3 and tokens[3].isdigit() else 1
        debug.spawn_item(player.inventory, item_name, quantity)
