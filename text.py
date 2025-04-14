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
    print("233...")

def play_menu():
    display_content = (
        "----------------------------------\n"
        "   W  - Walk\n"
        "   S  - See stats\n"
        "   A  - Aptitude\n"
        "   I  - Inventory\n"
        "   Q  - Quests\n"
        "   B  - Battle\n"
        "   Lr - Life recovery\n"
        "   Se - Show equipment\n"
        "   Sk - Show skills\n"
        "   Sg - Save game\n"
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
        f"      Anti CRT: {player.stats['anti_crit']}\n"
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
    print("==================================")

def show_equipment_info(player):
    print("=================================================")
    print("  EQUIPMENT")
    print("-------------------------------------------------")

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
        "       U  - Use an item\n"
        "       D  - Drop an item\n"
        "       E  - Equip an item           \n"
        "       Ua - Unequip all\n"
        "           Q - Quit\n"
        "----------------------------------"
    )
    print(display_inventory)

def combat_menu(player, allies, enemies):
    print("-------------------------------------------------")
    print(f"{player.name} - {fx.RED}HP: {player.stats['hp']}/{player.stats['max_hp']}{fx.END} - MP: {player.stats['mp']}/{player.stats['max_mp']} - CP: {player.combo_points}")
    for ally in allies:
        if ally != player:
            print(f"{ally.name} - {fx.RED}HP: {ally.stats['hp']}/{ally.stats['max_hp']}{fx.END}")
    for enemy in enemies:
        print(f"{enemy.name} - {fx.GREEN}HP: {enemy.stats['hp']}/{enemy.stats['max_hp']}{fx.END}")
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
        print(str(f"{index} - {spell.name} - {spell.cost}"))

def combo_menu(player):
    print("-------------------------------------------------")
    print("             COMBOS ['0' to Quit]")
    print("-------------------------------------------------")
    for index, combo in enumerate(player.combos, start=1):
        print(str(f"{index} - {combo.name} - {combo.cost}"))

def select_objective(target):
    print("-------------------------------------------------")
    print("             Select an objective:")
    print("-------------------------------------------------")
    for index, t in enumerate(target, start=1):
        print(f"{index} - {t.name} - HP: \033[32m{t.stats['hp']}/{t.stats['max_hp']}\033[0m")
    print("-------------------------------------------------")

def shop_menu(player):
    display_shop_menu_text = (
        "----------------------------------\n"
        f"          SHOP - 💰: {player.money}\n"
        "----------------------------------\n"
        "           B  - Buy Items\n"
        "           S  - Sell Items\n"
        "           T  - Talk\n"
        "           Ua - Unequip all\n"
        "           Si - Show inventory\n"
        "           E  - Exit\n"
        "----------------------------------\n"
    )
    print(display_shop_menu_text)

def shop_buy(player):
    display_shop_buy = (
        "----------------------------------\n"
        f"          SHOP - 💰: {player.money}\n"
        "           ['0' to Quit]\n"
        "----------------------------------\n"
    )
    print(display_shop_buy)


def show_skills(player):
    print("=== 法术技能 ===")
    if player.spells:
        for spell in player.spells:
            print(f"• {spell.name} - {spell.description} ({fx.GREEN}MP: {spell.cost}, Power: {spell.power}{fx.END})")
    else:
        print("暂无法术。")

    print("\n=== 组合技能 ===")
    if player.combos:
        for combo in player.combos:
            print(f"• {combo.name} - {combo.description} ({fx.YELLO}CP: {combo.cost}{fx.END})")
    else:
        print("暂无连招。")


def enter_shop(name):
    from data.event_text import rik_armor_shop_encounter, itz_magic_encounter
    if name == "里克的盔甲店":
        print(rik_armor_shop_encounter)
    elif name == "伊兹的魔法店":
        print(itz_magic_encounter)

def save_load_menu():
    """显示存档/读档菜单"""
    display_content = (
        "----------------------------------\n"
        "           S - Save game           \n"
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
    print(fx.bright_cyan("================"))
