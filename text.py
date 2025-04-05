
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
        "--------------------------------\n"
        "   1 - Battle\n"
        "   2 - See stats\n"
        "   3 - Assign aptitude points   \n"
        "   4 - Inventory\n"
        "   5 - Auto mode\n"
        "--------------------------------\n"
    )
    print(display_content)

def show_stats(player):
    stats_template = (
        f"----------------------------------\n"
        f"  STATS               💰: {player.money}\n"
        f"----------------------------------\n"
        f"      LV: {player.level}        EXP: {player.xp}/{player.xp_to_next_level}\n"
        f"      \033[31mHP: {player.stats['hp']}/{player.stats['max_hp']}\033[0m    \033[34mMP: {player.stats['mp']}/{player.stats['max_mp']}\033[0m\n"
        f"      ATK: {player.stats['atk']}        DEF: {player.stats['def']}\n"
        f"      MAT: {player.stats['mat']}        MDF: {player.stats['mdf']}\n"
        f"      AGI: {player.stats['agi']}        CRT: {player.stats['crit']}\n"
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

def show_aptitudes(player):
    display_aptitudes = (
        f"----------------------------------\n"
        f"  POINTS: {player.aptitude_points}\n"
        f"  SELECT AN APTITUDE\n"
        f"----------------------------------\n"
        f"      1 - STR (Current: {player.aptitudes['str']})\n"
        f"      2 - DEX (Current: {player.aptitudes['dex']})\n"
        f"      3 - INT (Current: {player.aptitudes['int']})\n"
        f"      4 - WIS (Current: {player.aptitudes['wis']})\n"
        f"      5 - CONST (Current: {player.aptitudes['const']})\n"
        f"      0 - Quit menu\n"
        f"----------------------------------\n"
    )
    print(display_aptitudes)

def inventory_menu():
    display_inventory = (
        "-------------------------------\n"
        "       S - Sell an item\n"
        "       D - Drop an item\n"
        "       E - Equip an item\n"
        "           Q - Quit\n"
        "-------------------------------"
    )
    print(display_inventory)

def combat_menu(player, enemy):
    display_combat = (
        "---------------------------------------\n"
        f"{player.name} - \033[31mHP: {player.stats['hp']}/{player.stats['max_hp']}\033[0m - MP: {player.stats['mp']}/{player.stats['max_mp']}\n"
        f"{enemy.name} - \033[32mHP: {enemy.stats['hp']}/{enemy.stats['max_hp']}\033[0m\n"
        "---------------------------------------\n"
        "       A - Attack  C - Combos          \n"
        "       S - Spells  D - Defense\n"
        "       E - Escape\n"
        "---------------------------------------\n"
    )
    print(display_combat)

def spell_menu(player):
    print("---------------------------------------")
    print("         SPELLS ['0' to Quit]")
    print("---------------------------------------")
    for index, spell in enumerate(player.spells, start=1):
        print(str(f"{index} - {spell.name}"))
