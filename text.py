import math

from test.clear_screen import clear_screen
import test.fx as fx


# *title_ui
def title_screen():
    display_content = (
        "-----------------------\n"
        "     Text RPG Game     \n"
        "-----------------------\n"
        "       1 - Play\n"
        "       2 - About\n"
        "       3 - Quit\n"
        "-----------------------\n"
    )
    print(display_content)

def help_menu():
    print("    游戏作者: kwo, 以及 GPT(可能还是他功劳大些)。\n\
参考项目: Python-Text-Turn-Based-RPG \n\
还有玩的开心, 以及学的开心。\n\
部分不懂的见 Git 标签: 最后的注释 \n\
好了, 你可以再次启动了。")

def play_menu():
    display_content = (
        "----------------------------------\n"
        "       W - Walk\n"
        "       S - See stats\n"
        "       A - Aptitude\n"
        "       I - Inventory\n"
        "       Q - Quests\n"
        "       M - Map\n"
        "----------------------------------\n"
    )
    print(display_content)


# *player_ui
def show_stats(player):
    stats_template = (
        f"==================================\n"
        f"  STATS               💰: {player.money}\n"
        f"----------------------------------\n"
        f"      LV: {player.level}          EXP: {player.xp}/{player.xp_to_next_level}\n"
        f"      {fx.RED}HP: {player.stats['hp']}/{player.stats['max_hp']}{fx.END}    {fx.BLUE}MP: {player.stats['mp']}/{player.stats['max_mp']}{fx.END}\n"
        f"      ATK: {player.stats['atk']}        DEF: {player.stats['def']}\n"
        f"      MAT: {player.stats['mat']}        MDF: {player.stats['mdf']}\n"
        f"      AGI: {player.stats['agi']}        LUK: {player.stats['luk']}\n"  
        f"----------------------------------\n"
        f"  APTITUDES\n"
        f"----------------------------------\n"
        f"      STR: {player.aptitudes['str']}        DEX: {player.aptitudes['dex']}\n"
        f"      INT: {player.aptitudes['int']}        WIS: {player.aptitudes['wis']}\n"
        f"      CONST: {player.aptitudes['const']}\n"
        f"----------------------------------\n"
        f"  EQUIPMENT\n"
        f"----------------------------------"
    )
    print(stats_template)
    for equipment in player.equipment:
        if player.equipment[equipment] is not None:
            print(f"    {equipment}: {player.equipment[equipment].name}")
        else:
            print(f"    {equipment}:")

def show_equipment_info(player):
    print("=================================================")
    print("  EQUIPMENT")
    fx.divider()

    for equipment in player.equipment:
        if player.equipment[equipment] is not None:
            print(f"    {player.equipment[equipment].show_info()}\n")
        else:
            print(f"    ---{equipment}---\n")

def show_aptitudes(player):
    display_aptitudes = (
        f"==================================\n"
        f"  POINTS: {player.aptitude_points}\n"
        f"  SELECT AN APTITUDE\n"
        f"----------------------------------\n"
        f"      1 - STR (Current: {player.aptitudes['str']})\n"
        f"      2 - DEX (Current: {player.aptitudes['dex']})\n"
        f"      3 - INT (Current: {player.aptitudes['int']})\n"
        f"      4 - WIS (Current: {player.aptitudes['wis']})\n"
        f"      5 - CONST (Current: {player.aptitudes['const']})\n"
        f"      Q - Quit menu\n"
        f"----------------------------------\n"
    )
    print(display_aptitudes)

def inventory_menu():
    display_inventory = (
        "       U  - Use an item\n"
        "       D  - Drop an item\n"
        "       E  - Equip an item\n"
        "       Q  - Quit\n"
        "================================================="
    )
    fx.divider()
    print(display_inventory)

def show_skills(player):
    print("========== Spell Skills ==========")
    if player.spells:
        for spell in player.spells:
            print(f"• {spell.name} - {spell.description} ({fx.GREEN}MP: {spell.cost}, Power: {spell.power}{fx.END})")
    else:
        print("暂无法术")
    print("\n========== Combo Skills ==========")
    if player.combos:
        for combo in player.combos:
            print(f"• {combo.name} - {combo.description} ({fx.YELLO}CP: {combo.cost}{fx.END})")
    else:
        print("暂无连招")


# *combat_ui
def combat_menu(player, allies, enemies):
    print("=================================================")
    print(f"【{player.name}】 Lv.{getattr(player, 'level', '?')} - CP: {player.combo_points}")
    print_status_bar("HP", player.stats['hp'], player.stats['max_hp'], fx.red)
    print_status_bar("MP", player.stats['mp'], player.stats['max_mp'], fx.blue)
    for ally in allies:
        if ally != player:
            print(f"【{ally.name}】 Lv.{getattr(ally, 'level', '?')}")
            print_status_bar("HP", ally.stats['hp'], ally.stats['max_hp'], fx.yellow)
    for enemy in enemies:
        print(f"【{enemy.name}】 Lv.{getattr(enemy, 'level', '?')}")
        print_status_bar("HP", enemy.stats['hp'], enemy.stats['max_hp'], fx.green)
    print("-------------------------------------------------")
    print("         A - Attack  C - Combos")
    print("         S - Spells  D - Defense             ")
    print("         E - Escape")
    print("-------------------------------------------------")

def print_status_bar(label, current, max_value, color_func):
    print("┌────────────────────┐")
    print(f"│{color_func(create_bar(current, max_value))}│{color_func(f' {label}: {current}/{max_value}')}")
    print("└────────────────────┘")

def spell_menu(player):
    print("=================================================")
    print("             SPELLS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, spell in enumerate(player.spells, start=1):
        print(str(f"{index} - {spell.name} - {spell.cost}"))

def combo_menu(player):
    print("=================================================")
    print("             COMBOS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, combo in enumerate(player.combos, start=1):
        print(str(f"{index} - {combo.name} - {combo.cost}"))

def select_objective(target):
    print("=================================================")
    print("             Select an objective:")
    print("-------------------------------------------------")
    for index, t in enumerate(target, start=1):
        print(f"{index} - {t.name} - HP: {fx.GREEN}{t.stats['hp']}/{t.stats['max_hp']}{fx.END}")
    print("-------------------------------------------------")


# *shop_ui
def shop_menu(player):
    display_shop_menu_text = (
        "=================================================\n"
        f"          SHOP - 💰: {player.money}\n"
        "-------------------------------------------------\n"
        "           B  - Buy Items\n"
        "           S  - Sell Items\n"
        "           T  - Talk\n"
        "           Ua - Unequip all\n"
        "           Si - Show inventory\n"
        "           E  - Exit"
    )
    print(display_shop_menu_text)
    fx.divider()

def shop_buy(player):
    display_shop_buy = (
        "=================================================\n"
        f"          SHOP - 💰: {player.money}\n"
        "           ['0' to Quit]"
    )
    print(display_shop_buy)
    fx.divider()

def enter_shop(name):
    import data.event_text as ev
    match name:
        case "里克的盔甲店": print(ev.rik_armor_shop_encounter)
        case "伊兹的魔法店": print(ev.itz_magic_encounter)
        case "安娜的防具店": print(ev.anna_armor_shop_encounter)
        case "杰克的武器店": print(ev.jack_weapon_shop_encounter)


def save_load_menu():
    display_content = (
        "----------------------------------\n"
        "           S - Save game\n"
        "           L - Load game\n"
        "           R - Return\n"
        "----------------------------------\n"
    )
    print(display_content)

def display_save_list(saves):
    """显示存档列表"""
    if not saves:
        print("没有找到存档")
        return
    print("----------------------------------")
    print(" 存档列表")
    print("----------------------------------")
    for i, save in enumerate(saves, 1):
        print(f" {i}. {save['player_name']} (等级 {save['level']}) - {save['date']}")
    print(" 0. 取消")
    print("----------------------------------")

def display_status_effects(battlers):
    print(fx.bright_cyan("==== Status effect ===="))
    for battler in battlers:
        if battler.buffs_and_debuffs:
            print(fx.cyan(f"{battler.name} 的状态: "))
            for effect in battler.buffs_and_debuffs:
                turns = effect.turns
                warn = "(即将结束)" if turns == 1 else ""
                print(f" - {effect.name}(剩余 {turns} 回合){warn}")
        else:
            print(f"{battler.name} 没有任何状态效果")
    print(fx.bright_cyan("======================="))


# *quest_ui
def show_all_quests(player):
    print(fx.bright_cyan("\n======= 任务列表 ======="))
    if player.active_quests:
        print("\n进行中的任务:")
        for i, q in enumerate(player.active_quests):
            print(f"{i+1}. {q.name} (推荐等级: {q.recommended_level})")
            print(f"   所在地区: {get_quest_region(q)}")
            print(f"   {q.description[:50]}..." if len(q.description) > 50 else f"   {q.description}")
    else:
        print("\n当前没有进行中的任务")
    if player.completed_quests:
        print("\n已完成的任务:")
        for i, q in enumerate(player.completed_quests):
            print(f"{i+1}. {q.name} [已完成]")
    else:
        print("\n尚未完成任何任务")
    print(fx.bright_cyan("\n========================"))
    print("\n输入q数字查看任务详情 (例如: q1), 或输入任意键返回")
    option = input("> ").lower()
    if option.startswith('q'):
        try:
            quest_idx = int(option[1:]) - 1
            if quest_idx >= 0 and quest_idx < len(player.active_quests):
                player.active_quests[quest_idx].show_info()
        except ValueError:
            pass


# *map_ui
def get_quest_region(quest_obj):
    """查找任务所在地区"""
    import map
    for region_name, region in map.world_map.regions.items():
        if quest_obj in region.quests:
            return region.name
    return "未知地区"

def map_menu(player):
    import map
    print(map.world_map.get_current_region_info())
    available_quests = map.world_map.show_region_quests(player)
    print("\n可前往地区:")
    print(map.world_map.list_available_regions())
    print("\n1-N. 前往对应编号的地区\nq. 返回主菜单")

    if available_quests:
        print("t+数字, 接受任务(例如: t1)")

    option = input("> ").lower()
    if option == "q":
        return

    if option.startswith('t') and available_quests:
        try:
            quest_idx = int(option[1:]) - 1
            map.world_map.accept_quest(player, quest_idx, available_quests)
        except ValueError:
            print("无效的任务选择")

    else:
        try:
            idx = int(option) - 1
            if 0 <= idx < len(map.world_map.regions):
                region_key = list(map.world_map.regions.keys())[idx]
                map.world_map.change_region(region_key)
                clear_screen()
                print(f"\n你已经抵达 {map.world_map.current_region.name}\n")
                print(map.world_map.current_region.description)
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的命令")


def debug_show_stats(player):
    display_stats = (
        f"===== {player.name} 的详细数据 =====\n"
        f"等级: {player.level} ({player.xp}/{player.xp_to_next_level} XP)\n"
        f"职业: {player.class_name}\n"
        f"金钱: {player.money} 枚硬币\n"
        f"生命值: {player.stats['hp']}/{player.stats['max_hp']}\n"
        f"魔法值: {player.stats['mp']}/{player.stats['max_mp']}\n"
        f"\n--- 战斗属性 ---\n"
        f"攻击力: {player.stats['atk']}\n"
        f"防御力: {player.stats['def']}\n"
        f"魔法攻击: {player.stats['mat']}\n"
        f"魔法防御: {player.stats['mdf']}\n"
        f"敏捷: {player.stats['agi']}\n"
        f"幸运: {player.stats['luk']}\n"
        f"暴击倍率: {player.stats['crit']}\n"
        f"抗暴击: {player.stats['anti_crit']}\n"
        f"\n可用能力点: {player.aptitude_points}\n"
    )
    print(display_stats)

def backpack_item_stats(inv):
    print("=== 背包物品统计 ===")
    item_counts = {'Equipment': 0, 'Potion': 0, 'Jewel': 0, 'Grimoire': 0, 'Other': 0}
    for item in inv.items:
        item_type = type(item).__name__
        if item_type in item_counts:
            item_counts[item_type] += item.amount
        else:
            item_counts['Other'] += item.amount

    total_items = sum(item_counts.values())
    print(f"装备: {item_counts['Equipment']} 件")
    print(f"药水: {item_counts['Potion']} 瓶")
    print(f"宝石: {item_counts['Jewel']} 个")
    print(f"魔法书: {item_counts['Grimoire']} 本")
    print(f"其他物品: {item_counts['Other']} 个")
    print(f"\n总计: {total_items} 件物品")

def create_bar(value, max_value, width=20, char="█", empty_char="░"):
    """创建一个文本进度条"""
    if max_value <= 0:
        return empty_char * width

    fill_width = int(width * (value / max_value))
    return char * fill_width + empty_char * (width - fill_width)

def display_battle_stats(attacker, defender):
    from data.constants import DEBUG
    """显示两个战斗者的对比状态"""
    if not DEBUG:
        return

    atk_def_ratio = attacker.stats["atk"] / max(1, defender.stats["def"])
    mat_mdf_ratio = attacker.stats["mat"] / max(1, defender.stats["mdf"])
    speed_diff = attacker.stats["agi"] - defender.stats["agi"]

    print("\n====== 战斗状态分析 ======")
    print(f"【{attacker.name}】 Lv.{getattr(attacker, 'level', '?')}")
    print(f"HP: {attacker.stats['hp']}/{attacker.stats['max_hp']} ")
    print(f"MP: {attacker.stats['mp']}/{attacker.stats['max_mp']} ")
    print(f"\n【{defender.name}】 Lv.{getattr(defender, 'level', '?')}")
    print(f"HP: {defender.stats['hp']}/{defender.stats['max_hp']} ")

    print("\n----- 数值对比 -----")
    print(f"物理攻防比: {atk_def_ratio:.2f}x " + ("(优势)" if atk_def_ratio > 1 else "(劣势)"))
    print(f"魔法攻防比: {mat_mdf_ratio:.2f}x " + ("(优势)" if mat_mdf_ratio > 1 else "(劣势)"))
    print(f"速度差: {speed_diff:+d} " + ("(更快)" if speed_diff > 0 else "(更慢)" if speed_diff < 0 else "(相同)"))

    est_phys_dmg = max(1, attacker.stats["atk"]*4 - defender.stats["def"]*2.5)
    est_mag_dmg = max(1, attacker.stats["mat"]*3 - defender.stats["mdf"]*1.5)

    print(f"\n预估每回合物理伤害: {est_phys_dmg:.1f}")
    print(f"预估每回合魔法伤害: {est_mag_dmg:.1f}")
    print(f"预估击杀回合数: {math.ceil(defender.stats['hp'] / max(est_phys_dmg, est_mag_dmg))}")
    print("========================\n")
