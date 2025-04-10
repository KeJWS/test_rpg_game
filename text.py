import test.fx as fx

def title_screen():
    display_content = (
        "-----------------------\n"
        "     Text RPG Game     \n"
        "-----------------------\n"
        "       1 - Play        \n"
        "       2 - Help        \n"
        "       3 - Quit        \n"
        "-----------------------\n"
    )
    print(display_content)

def help_menu():
    print("")

def play_menu():
    display_content = (
        "----------------------------------\n"
        "   1 - Battle\n"
        "   2 - See stats\n"
        "   3 - Assign aptitude points      \n"
        "   4 - Inventory\n"
        "   5 - Full heal\n"
        "   6 - Save system\n"
        "----------------------------------\n"
    )
    print(display_content)

def show_stats(player):
    stats_template = (
        f"==================================\n"
        f"  STATS               💰: {player.money}\n"
        f"----------------------------------\n"
        f"      LV: {player.level}          EXP: {player.xp}/{player.xp_to_next_level}\n"
        f"      {fx.RED}HP: {player.stats['hp']}/{player.stats['max_hp']}{fx.END}    {fx.BLUE}MP: {player.stats['mp']}/{player.stats['max_mp']}{fx.END}\n"
        f"      ATK: {player.stats['atk']}        DEF: {player.stats['def']}\n"
        f"      MAT: {player.stats['mat']}        MDF: {player.stats['mdf']}\n"
        f"      AGI: {player.stats['agi']}        CRT: {player.stats['crit']}%\n"
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
    eq = player.equipment
    slots = [
        ("weapon", "shield"),
        ("head", "armor"),
        ("hand", "foot")
    ]
    for left, right in slots:
        left_eq = eq[left].name if eq[left] else None
        right_eq = eq[right].name if eq[right] else None
        print(f"    {left}: {left_eq}   {right}: {right_eq}")
    print(f"    accessory: {eq["accessory"].name if eq["accessory"] else None}")
    print("==================================")

def show_equipment_info(player):
    print("==================================")
    print("  EQUIPMENT")
    print("----------------------------------")

    for equipment in player.equipment:
        if player.equipment[equipment] is not None:
            print(f"    {player.equipment[equipment].show_info()}")
        else:
            print(f"    ---None---")

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
        "----------------------------------\n"
        "       U - Use an item\n"
        "       S - Sell an item\n"
        "       D - Drop an item\n"
        "       E - Equip an item           \n"
        "           Q - Quit\n"
        "----------------------------------"
    )
    print(display_inventory)

def combat_menu(player, enemies):
    print("-------------------------------------------------")
    print(f"{player.name} - \033[31mHP: {player.stats['hp']}/{player.stats['max_hp']}\033[0m - MP: {player.stats['mp']}/{player.stats['max_mp']} - CP: {player.combo_points}")
    for enemy in enemies:
        print(f"{enemy.name} - \033[32mHP: {enemy.stats['hp']}/{enemy.stats['max_hp']}\033[0m")
    print("-------------------------------------------------")
    print("             A - Attack  C - Combos")
    print("             S - Spells  D - Defense             ")
    print("             E - Escape")
    print("-------------------------------------------------")

def spell_menu(player):
    print("-------------------------------------------------")
    print("             SPELLS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, spell in enumerate(player.spells, start=1):
        print(str(f"{index} - {spell.name}"))

def combo_menu(player):
    print("-------------------------------------------------")
    print("             COMBOS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, c in enumerate(player.combos, start=1):
        print(str(f"{index} - {c.name}"))

def select_objective(target):
    print("-------------------------------------------------")
    print("             Select an objective:")
    print("-------------------------------------------------")
    for index, t in enumerate(target, start=1):
        print(f"{index} - {t.name} - HP: \033[32m{t.stats['hp']}/{t.stats['max_hp']}\033[0m")
    print("-------------------------------------------------")

def save_load_menu():
    """显示存档/读档菜单"""
    display_content = (
        "----------------------------------\n"
        "           1 - Save game           \n"
        "           2 - Load game\n"
        "           3 - Delete save\n"
        "           0 - Return\n"
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
    import test.fx as fx
    print(fx.bright_cyan("=== 状态效果 ==="))
    for battler in battlers:
        if battler.buffs_and_debuffs:
            print(fx.cyan(f"{battler.name} 的状态: "))
            for effect in battler.buffs_and_debuffs:
                turns = effect.turns
                warn = "(即将结束)" if turns == 1 else ""
                print(f" - {effect.name}(剩余 {turns} 回合){warn}")
        else:
            print(f"{battler.name} 没有任何状态效果")
    print(fx.bright_cyan("=== 状态效果 ==="))

def log_battle_result(result: str, player, enemies):
    from datetime import datetime
    with open("data/battle_log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"=== 战斗记录: {timestamp} ===\n")
        f.write(f"结果: {result}\n")
        f.write(f"玩家: {player.name} 等级{player.level} HP {player.stats['hp']}/{player.stats['max_hp']}\n")
        f.write("敌人:\n")
        for enemy in enemies:
            f.write(f"- {enemy.name} 经验 {enemy.xp_reward}, 金币 {enemy.gold_reward}\n")
        f.write("\n")
