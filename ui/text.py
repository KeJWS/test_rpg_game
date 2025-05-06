import math

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from test.clear_screen import clear_screen

console = Console()


# *title_ui
def title_screen():
    pannel = Panel.fit(
        Text("\nText RPG Game\n\n1 - Play\n2 - About\n3 - Quit\n", justify="center"),
        title="Use number keys to select",
        subtitle="welcome",
        border_style="bold green",
    )
    console.print(pannel)

def help_menu():
    print("    游戏作者: kwo, 以及 GPT(可能还是他功劳大些)。\n\
参考项目: Python-Text-Turn-Based-RPG \n\
还有玩的开心, 以及学的开心。\n\
部分不懂的见 Git 标签: 最后的注释 \n\
好了, 你可以再次启动了。")

def play_menu():
    pannel = Panel.fit(
        Text("\nText RPG Game\n\nW - Walk\nS - See stats\nA - Aptitude\nI - Inventory\nQ - Quests\nM - Map\n", justify="center"),
        title="Use letter keys to select",
        subtitle="Main Interface",
        border_style="bold green",
    )
    console.print(pannel)


# *player_ui
def show_stats(player):
    table = Table(title=f"{player.name}'s Stats", box=box.ROUNDED, border_style="bold green")
    table.add_column("Attribute", justify="right")
    table.add_column("Value", justify="left")
    table.add_row("LV", f"{player.ls.level}")
    table.add_row("EXP", f"{player.ls.xp}/{player.ls.xp_to_next_level}")
    table.add_row("Money", f"[yellow]{player.money}[/yellow] 💰")
    table.add_row("Hunger", f"[yellow]{player.stats['hunger']}[/yellow]/[yellow]{player.stats['max_hunger']}[/yellow]")
    table.add_row("HP", f"[green]{player.stats['hp']}[/green]/[green]{player.stats['max_hp']}[/green]")
    table.add_row("MP", f"[blue]{player.stats['mp']}[/blue]/[blue]{player.stats['max_mp']}[/blue]")
    table.add_row("ATK / DEF", f"{player.stats['atk']} / {player.stats['def']}")
    table.add_row("MAT / MDF", f"{player.stats['mat']} / {player.stats['mdf']}")
    table.add_row("AGI / LUK", f"{player.stats['agi']} / {player.stats['luk']}")
    console.print(table)

    aptitudes = Table(title="Aptitudes", box=box.ROUNDED, border_style="bold green")
    aptitudes.add_column("Name")
    aptitudes.add_column("Value")
    for k, v in player.aptitudes.items():
        aptitudes.add_row(k.upper(), str(v))
    console.print(aptitudes)

    eq_table = Table(title="Equipment", box=box.ROUNDED, border_style="bold green")
    eq_table.add_column("Slot")
    eq_table.add_column("Item")
    for slot, item in player.equipment.items():
        eq_table.add_row(slot, item.name if item else "-")
    console.print(eq_table)

def inventory_menu():
    pannel = Panel.fit(
        Text("\nU - Use an item\nD - Drop an item\nE - Equip an item\nQ - Quit\n", justify="center"),
        title="Use letter keys to select",
        subtitle="Inventory",
        border_style="bold green",
    )
    console.print(pannel)

def show_equipment_info(player):
    print("=================================================")
    print("  EQUIPMENT")
    print("-------------------------------------------------")

    for equipment in player.equipment:
        if player.equipment[equipment] is not None:
            console.print(f"    {player.equipment[equipment].show_info()}\n")
        else:
            console.print(f"    ---{equipment}---\n")

def show_aptitudes(player):
    pannel = Panel.fit(
        Text(
        f"\n1 - STR (Current: {player.aptitudes['str']})\n"
        f"2 - DEX (Current: {player.aptitudes['dex']})\n"
        f"3 - INT (Current: {player.aptitudes['int']})\n"
        f"4 - WIS (Current: {player.aptitudes['wis']})\n"
        f"5 - CONST (Current: {player.aptitudes['const']})\n"
        f"Q - Quit menu\n",
        justify="left"
        ),
        title="Select an aptitude",
        subtitle=f"Point: {player.ls.aptitude_points}",
        border_style="bold green"
    )
    console.print(pannel)

def show_skills(player):
    spell_table = Table(title="Spells", box=box.SIMPLE)
    spell_table.add_column("Name", style="magenta")
    spell_table.add_column("Cost")
    spell_table.add_column("Power")
    spell_table.add_column("Description")

    for spell in player.spells:
        spell_table.add_row(spell.name, str(spell.cost), str(spell.power), spell.description)

    combo_table = Table(title="Combos", box=box.SIMPLE)
    combo_table.add_column("Name", style="yellow")
    combo_table.add_column("Cost")
    combo_table.add_column("Description")

    for combo in player.combos:
        combo_table.add_row(combo.name, str(combo.cost), combo.description)

    console.print(spell_table)
    console.print(combo_table)


# *combat_ui
def combat_menu(player, allies, enemies) -> None:
    print("=================================================")
    print(f"【{player.name}】 Lv.{getattr(player.ls, 'level', '?')} - CP: {player.combo_points}")
    print_status_bar("HP", player.stats['hp'], player.stats['max_hp'], "green")
    print_status_bar("MP", player.stats['mp'], player.stats['max_mp'], "blue")
    for ally in allies:
        if ally != player:
            print(f"【{ally.name}】 Lv.{getattr(ally, 'level', '?')}")
            print_status_bar("HP", ally.stats['hp'], ally.stats['max_hp'], "yellow")
    for enemy in enemies:
        print(f"【{enemy.name}】 Lv.{getattr(enemy, 'level', '?')}")
        print_status_bar("HP", enemy.stats['hp'], enemy.stats['max_hp'], "red")
    print("-------------------------------------------------")
    print("         A - Attack  C - Combos")
    print("         S - Spells  D - Defense                 ")
    print("         Q - Quit")
    print("-------------------------------------------------")

def print_status_bar(label, current, max_value, color: str):
    bar_len = 20
    filled_len = int(bar_len * current / max_value)
    bar = f"[{color}]{'█' * filled_len}[/{color}]{'.' * (bar_len - filled_len)}"
    console.print(f"{label}: {bar} {current}/{max_value}")

def spell_menu(player) -> None:
    print("=================================================")
    print("             SPELLS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, spell in enumerate(player.spells, start=1):
        console.print(str(f"{index} - {spell.name} - MP: {spell.cost}"))

def combo_menu(player) -> None:
    print("=================================================")
    print("             COMBOS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, combo in enumerate(player.combos, start=1):
        console.print(str(f"{index} - {combo.name} - CP: {combo.cost}"))

def select_objective(targets: List) -> None:
    print("=================================================")
    print("             Select an objective:")
    print("-------------------------------------------------")
    for index, t in enumerate(targets, start=1):
        hp_percent = round(t.stats["hp"] / t.stats["max_hp"] * 100)
        console.print(f"{index} - {t.name} - HP: [red]{t.stats['hp']}/{t.stats['max_hp']}[/red] ({hp_percent}%)")
    print("-------------------------------------------------")

def display_status_effects(battlers: List) -> None:
    console.print("==== Status effect ====", style="bold green")
    for battler in battlers:
        if battler.buffs_and_debuffs:
            console.print(f"{battler.name} 的状态: ", style="green")
            for effect in battler.buffs_and_debuffs:
                turns = effect.turns
                warn = "(即将结束)" if turns == 1 else ""
                print(f" - {effect.name}(剩余 {turns} 回合){warn}")
        else:
            print(f"{battler.name} 没有任何状态效果")
    console.print("=======================", style="bold green")


# *shop_ui
def shop_menu(player):
    pannel = Panel.fit(
        Text("\nB - Buy Items\nS - Sell Items\nT - Talk\nUa - Unequip all\nSi - Show inventory\nQ - Quit\n", justify="left"),
        title="Use letter keys to select",
        subtitle=f"SHOP - 💰: {player.money}",
        border_style="bold green",
    )
    console.print(pannel)

def shop_buy(player):
    display_shop_buy = (
        "=================================================\n"
        f"          SHOP - 💰: {player.money}\n"
        "           ['0' to Quit]\n"
        "-------------------------------------------------\n"
    )
    print(display_shop_buy)

def enter_shop(name):
    import data.event_text as ev
    match name:
        case "里克的盔甲店": print(ev.rik_armor_shop_encounter)
        case "伊兹的魔法店": print(ev.itz_magic_encounter)
        case "安娜的防具店": print(ev.anna_armor_shop_encounter)
        case "杰克的武器店": print(ev.jack_weapon_shop_encounter)
        case "青铜匠武具店": print(ev.lok_armor_shop_encounter)
        case "玛丽的小吃摊": print(ev.mary_food_stall_encounter)


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


# *quest_ui
def show_all_quests(player):
    console.print("\n======= 任务列表 =======", style="bold green")
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
    console.print("\n========================", style="bold green")
    print("\n输入 q1 查看任务1详情, 输入 c1 交付任务1")
    option = input("> ").lower()
    if option.startswith('q'):
        try:
            quest_idx = int(option[1:]) - 1
            if quest_idx >= 0 and quest_idx < len(player.active_quests):
                player.active_quests[quest_idx].show_info(player)
        except ValueError:
            pass
    elif option.startswith('c'):
        try:
            quest_idx = int(option[1:]) - 1
            if quest_idx >= 0 and quest_idx < len(player.active_quests):
                player.active_quests[quest_idx].try_complete_collection(player)
        except ValueError:
            pass


# *map_ui
def get_quest_region(quest_obj):
    """查找任务所在地区"""
    import world.map as map
    for region_name, region in map.world_map.regions.items():
        if quest_obj in region.quests:
            return region.name
    return "未知地区"

def map_menu(player):
    import world.map as map
    map.world_map.get_current_region_info()
    available_quests = map.world_map.show_region_quests(player)
    print()
    map.world_map.list_available_regions()
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
    table = Table(title=f"[bold]{player.name}[/bold] 状态", box=box.ROUNDED)
    table.add_column("属性", style="bold cyan")
    table.add_column("数值", style="bold white")
    table.add_row("等级", str(player.ls.level))
    table.add_row("经验", f"{player.ls.xp}/{player.ls.xp_to_next_level}")
    table.add_row("职业", f"{player.ls.class_name}")
    table.add_row("金钱", f"[yellow]{player.money}G[/yellow]")
    table.add_row("HP", f"[green]{player.stats['hp']}/{player.stats['max_hp']}[/green]")
    table.add_row("MP", f"[blue]{player.stats['mp']}/{player.stats['max_mp']}[/blue]")
    table.add_row("攻击 / 防御", f"{player.stats['atk']} / {player.stats['def']}")
    table.add_row("魔攻 / 魔防", f"{player.stats['mat']} / {player.stats['mdf']}")
    table.add_row("敏捷 / 幸运", f"{player.stats['agi']} / {player.stats['luk']}")
    table.add_row("暴击", str(player.stats["crit"]))
    table.add_row("抗暴击", str(player.stats["anti_crit"]))
    table.add_row("能力点", str(player.ls.aptitude_points))
    console.print(table)

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
