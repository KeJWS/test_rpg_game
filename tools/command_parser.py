from inventory import Inventory_interface as interface
from test.clear_screen import clear_screen, enter_clear_screen
from save_system import save_game, get_save_list, load_game
from tools import dev_tools as debug

from data.constants import DEBUG

import events, text

def show_help(topic=None):
    command_docs = {
    "p": """
玩家相关命令:
    p --help    查看玩家指令帮助
    p -hp       显示玩家当前血量
    p -mp       显示玩家当前魔法值
    p -gold     显示玩家当前金币
    p -lr       生命恢复水晶
    p -se       查看玩家装备
    p -sk       查看玩家技能
    p -sg       测试性存档功能
    p --bag     查看背包[debug]
""",
    "p.i": """
玩家背包相关命令:
    p.i --help      查看玩家背包指令帮助
    p.i -u          使用物品
    p.i -d          丢弃物品
    p.i -e          装备物品
    p.i -ua         卸下全部装备
    p.i -c          比较装备
    p.i -vi         查看物品详情
    p.i -si         查看背包物品
    p.i --give_all  全物品[debug]
""",
    "p.gold": "p.gold amount    刷 amount 数量金币[debug]",
    "p.exp": "p.exp amount    刷 amount 数量经验[debug]",
    "default": "可用主题: p\n例如: p --help",
}

    print(command_docs.get(topic, command_docs["default"]))
    enter_clear_screen()

def handle_command(command: str, player):
    from tools import dev_tools
    tokens = command.strip().split()
    if not tokens:
        print("请输入命令（输入 p --help 查看帮助）")
        enter_clear_screen()
        return

    main = tokens[0]
    sub = None
    if "." in main:
        main, sub = main.split(".", 1)

    if main == "p":
        if sub is None:
            if len(tokens) == 1 or tokens[1] == "--help":
                show_help("p")
                return
            subcommand = tokens[1]
            match subcommand:
                case "-hp": print(f"HP: {player.stats['hp']}/{player.stats['max_hp']}")
                case "-mp": print(f"MP: {player.stats['mp']}/{player.stats['max_mp']}")
                case "-gold": print(f"💰: {player.gold}")
                case "-lr": clear_screen(); events.life_recovery_crystal(player); enter_clear_screen()
                case "-se": clear_screen(); text.show_equipment_info(player); enter_clear_screen()
                case "-sk": clear_screen(); text.show_skills(player); enter_clear_screen()
                case "-sg":
                    clear_screen()
                    text.save_load_menu()
                    save_option = input("> ").lower()
                    if save_option == "s":
                        save_name = input("输入存档名 (留空使用默认名称): ")
                        if not save_name.strip():
                            save_name = None
                        p.unequip_all()
                        save_metadata = save_game(p, save_name)
                        print(f"游戏已保存: {save_metadata['name']}")
                    elif save_option == "l":
                        saves = get_save_list()
                        text.display_save_list(saves)
                        save_index = int(input("> "))
                        if save_index > 0 and save_index <= len(saves):
                            loaded_player = load_game(saves[save_index-1]['name'])
                            if loaded_player:
                                p = loaded_player
                                print(f"游戏已加载: {loaded_player.name} (等级: {loaded_player.level}, 职业: {loaded_player.class_name})")
                    enter_clear_screen()
                case "--bag": dev_tools.handle_debug_command("bag", player.inventory); enter_clear_screen()
                case _: print(f"未知的玩家指令: {tokens[1]}"); show_help("p")
        elif sub == "i":
            if len(tokens) < 2:
                show_help("p.i")
                return
            inv = player.inventory
            subcommand = tokens[1]
            match subcommand:
                case "-u": clear_screen(); player.use_item(interface(inv).use_item())
                case "-d": clear_screen(); interface(inv).drop_item()
                case "-e": clear_screen(); player.equip_item(interface(inv).equip_item())
                case "-ua": clear_screen(); player.unequip_all()
                case "-c": clear_screen(); interface(inv).compare_equipment()
                case "-vi": clear_screen(); player.view_item_detail(interface(inv).view_item())
                case "-si": clear_screen(); inv.show_inventory_item()
                case "--help": show_help("p.i")
                case "--give_all": dev_tools.handle_debug_command("give_all", inv); enter_clear_screen()
                case _: print(f"未知的 p.i 背包指令: {subcommand}"); show_help("p.i")
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

    else:
        debug.debug_print(f"未知命令模块: {tokens[0]}")
        enter_clear_screen()
        return command
