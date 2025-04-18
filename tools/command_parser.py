from inventory import Inventory_interface as interface
from test.clear_screen import clear_screen, enter_clear_screen
from tools.save_system import save_game, get_save_list, load_game
from tools import dev_tools as debug

from data.constants import DEBUG
import events, text
from extensions import shops 

import data.debug_help

def show_help(topic=None):
    command_docs = data.debug_help.command_docs
    print(command_docs.get(topic, command_docs["default"]))
    enter_clear_screen()

def handle_command(command: str, player):
    tokens = command.strip().split()
    if not tokens:
        print("请输入命令（输入 p --help 查看帮助）")
        enter_clear_screen()
        return

    main = tokens[0]
    sub = None
    if "." in main:
        main, sub = main.split(".", 1)

    shop_dict = {
        "jack": events.shop_jack_weapon,
        "anna": events.shop_anna_armor,
        "rik": events.shop_rik_armor,
        "itz": events.shop_itz_magic
    }

    if main == "p":
        if sub is None:
            handle_p_command(tokens, player)
        elif sub == "i":
            handle_pi_command(tokens, player)
        elif sub == "gold":
            if tokens[1].isdigit() and DEBUG:
                amount = int(tokens[1])
                player.add_money(amount)
                enter_clear_screen()
        elif sub == "exp":
            if tokens[1].isdigit() and DEBUG:
                amount = int(tokens[1])
                player.add_exp(amount)
                enter_clear_screen()
        else:
            debug.debug_print(f"未知 p 命令模块: {main}")
            enter_clear_screen()
            return command

    elif main in shop_dict and DEBUG:
        if sub == "i":
            handle_shop_command(main, shop_dict[main], tokens, player)

    else:
        debug.debug_print(f"未知命令模块: {tokens[0]}")
        enter_clear_screen()
        return command

def handle_save_load(player):
    text.save_load_menu()
    save_option = input("> ").lower()
    if save_option == "s":
        save_name = input("输入存档名 (留空使用默认名称): ").strip() or None
        player.unequip_all()
        save_metadata = save_game(player, save_name)
        print(f"游戏已保存: {save_metadata['name']}")
    elif save_option == "l":
        saves = get_save_list()
        text.display_save_list(saves)
        save_index = int(input("> "))
        if 0 < save_index <= len(saves):
            loaded_player = load_game(saves[save_index-1]['name'])
            if loaded_player:
                print(f"游戏已加载: {loaded_player.name} (等级: {loaded_player.level}, 职业: {loaded_player.class_name})")
                return loaded_player
    enter_clear_screen()
    return player

def handle_shop_command(shop_name, shop_data, tokens, player):
    if tokens[1] == "--buy":
        clear_screen()
        vendor = shops.Shop(shop_data.item_set)
        player.buy_from_vendor(vendor)

def handle_p_command(tokens, player):
    subcommand_map = {
        "-hp": lambda: print(f"HP: {player.stats['hp']}/{player.stats['max_hp']}"),
        "-mp": lambda: print(f"MP: {player.stats['mp']}/{player.stats['max_mp']}"),
        "-gold": lambda: print(f"💰: {player.gold}"),
        "-lr": lambda: (clear_screen(), events.life_recovery_crystal(player), enter_clear_screen()),
        "-se": lambda: (clear_screen(), text.show_equipment_info(player), enter_clear_screen()),
        "-sk": lambda: (clear_screen(), text.show_skills(player), enter_clear_screen()),
        "--bag": lambda: (debug.handle_debug_command("bag", player.inventory), enter_clear_screen()),
        "-sg": lambda: handle_save_load(player),
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
        "-u": lambda: (clear_screen(), player.use_item(interface(inv).use_item())),
        "-d": lambda: (clear_screen(), interface(inv).drop_item()),
        "-e": lambda: (clear_screen(), player.equip_item(interface(inv).equip_item())),
        "-ua": lambda: (clear_screen(), player.unequip_all()),
        "-c": lambda: (clear_screen(), interface(inv).compare_equipment()),
        "-vi": lambda: (clear_screen(), player.view_item_detail(interface(inv).view_item())),
        "-si": lambda: (clear_screen(), inv.show_inventory_item()),
        "--help": lambda: show_help("p.i"),
        "--give_all": lambda: (debug.handle_debug_command("give_all", inv), enter_clear_screen()),
    }

    if len(tokens) == 1 or tokens[1] == "--help":
        show_help("p.i")
        return

    func = subcommand_map.get(tokens[1])
    if func:
        func()
    else:
        debug.debug_print(f"未知的 p.i 玩家指令: {tokens[1]}")
        show_help("p.i")
