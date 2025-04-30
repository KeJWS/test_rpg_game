from data.constants import DEBUG

import events
import data.debug_help
import ui.text as text
from extensions import shops
from tools import dev_tools as debug
from inventory import Inventory_interface as interface
from enemies import enemy_data
from test.clear_screen import clear_screen, enter_clear_screen, screen_wrapped

SHOP_DICT = {
    # "jack": events.shop_jack_weapon,
    # "anna": events.shop_anna_armor,
    # "rik": events.shop_rik_armor,
    # "itz": events.shop_itz_magic
}

@screen_wrapped
def show_help(topic=None):
    command_docs = data.debug_help.command_docs
    print(command_docs.get(topic, command_docs["default"]))

def handle_command(command: str, player):
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
            case "ap": player.aptitude_points += int(tokens[1]) if tokens[1].isdigit() and DEBUG else None; enter_clear_screen()
            case _: debug.debug_print(f"未知 p 命令模块: {main}"); enter_clear_screen(); return command

    elif main in SHOP_DICT and DEBUG:
        if sub == "i":
            handle_shop_command(main, SHOP_DICT[main], tokens, player)

    elif main == "a" and sub == "d":
        if len(tokens) >= 3 and tokens[1] == "-db":
            enemy_name = tokens[2]
            if enemy_name in enemy_data:
                enemy = enemy_data[enemy_name].clone()
                clear_screen()
                text.display_battle_stats(player, enemy)
                enter_clear_screen()
    else:
        if DEBUG:
            debug.debug_print(f"未知命令模块: {tokens[0]}")
            enter_clear_screen()
        return command

def handle_shop_command(shop_name, shop_data, tokens, player):
    if tokens[1] == "-buy":
        clear_screen()
        vendor = shops.Shop(shop_data.item_set)
        player.buy_from_vendor(vendor)

def handle_p_command(tokens, player):
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
    inv = player.inventory
    subcommand_map = {
        "-U": screen_wrapped(lambda: player.use_item(interface(inv).use_item())),
        "-D": screen_wrapped(lambda: interface(inv).drop_item()),
        "-E": screen_wrapped(lambda: player.equip_item(interface(inv).equip_item())),
        "-C": screen_wrapped(lambda: interface(inv).compare_equipment()),
        "-ua": screen_wrapped(lambda: player.unequip_all()),
        "-vi": screen_wrapped(lambda: player.view_item_detail(interface(inv).view_item())),
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
    if not DEBUG:
        return
    if len(tokens) > 2 and tokens[2].isdigit():
        target_level = int(tokens[2])
        current_level = player.level
        if target_level > current_level:
            for _ in range(target_level - current_level):
                player.add_exp(player.xp_to_next_level)

def handle_spawn_item_command(tokens, player):
    if len(tokens) >= 3:
        item_name = tokens[2]
        quantity = int(tokens[3]) if len(tokens) > 3 and tokens[3].isdigit() else 1
        debug.spawn_item(player.inventory, item_name, quantity)
