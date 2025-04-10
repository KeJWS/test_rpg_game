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
        "   1 - Walk\n"
        "   2 - See stats\n"
        "   3 - Aptitude\n"
        "   4 - Inventory\n"
        "   5 - Save system\n"
        "   6 - Show equipment info\n"
        "   7 - Battle\n"
        "   8 - Quests\n"
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
    print(f"    accessory: {eq['accessory'].name if eq['accessory'] else None}")
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
        "           B - Buy Items\n"
        "           S - Sell Items\n"
        "           T - Talk\n"
        "           E - Exit\n"
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

def enter_shop(name):
    if name == "里克的盔甲店":
        print(rik_armor_shop_encounter)
    elif name == "伊兹的魔法店":
        print(itz_magic_encounter)

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


### 事件文本

# 初始事件
initial_event_text = '这一天终于到来了。你已在冒险者公会登记了自己的姓名。\n\
作为礼物，他们允许你从六套装备中选择一套。你会选择哪一套？\n\
1 - 战士套装\n\
2 - 盗贼套装\n\
3 - 魔法师套装'

## 商店

# 里克的盔甲店
rik_armor_shop_encounter = "在一个小村庄四处游荡时，你发现自己站在一家店铺前。\n\
门上挂着一块招牌，上面写着：<里克的护甲店>。\n\
要进入吗？[y/n]"
rik_armor_shop_enter = "“你好，朋友！你需要点什么？” 一个身材魁梧的男子问道。\n"
rik_armor_shop_talk = "“我这里有各种护甲，适合不同的战士。” 里克笑着说。\n"
rik_armor_shop_exit = "你离开了村庄，继续踏上冒险之旅。\n"

# 伊兹的魔法店
itz_magic_encounter = "你误入了一片沼泽。环顾四周，你发现一座小屋。\n\
门上挂着一块招牌，上面写着：<伊兹的魔法店>。\n\
要进入吗？[y/n]"
itz_magic_enter = "屋内站着一位戴着厚重眼镜的矮小女子，她看上去像是一位女巫。\n\
她低声呢喃道：“哦？看看是谁来了……来吧，随意看看！”\n"
itz_magic_talk = "“嗯，我能感觉到你身上有一些特殊的气息。” 伊兹微微抬起头，眯眼看着你。\n\
“这里有各式各样的法术书，草药，还有一些你可能需要的魔法物品。” 她指向架子上堆满了书籍和瓶瓶罐罐的地方。\n"
itz_magic_exit = "你离开了沼泽，继续踏上旅程。\n"


## 治疗

# 美杜莎神像
medussa_statue_encounter = "在一座山丘的顶端，你发现了一座小型神殿。\n\
这里矗立着一尊古老而被遗忘的女神雕像。\n\
不知为何，你心生敬意，想要向它致敬。\n\
是否跪拜？[y/n]"
medussa_statue_success = "你感受到一股温暖的力量流遍全身。\n"
medussa_statue_fail = "什么也没有发生，或许只是你的错觉。\n"
medussa_statue_refuse = "你决定不跪拜。\n"

## 任务
quest_caesarus_bandit_text = "凯撒鲁斯和他的匪徒一直在\n\
骚扰附近的村庄。去解决他们吧。"
shop_quest_caesarus_bandits = "听说过那群强盗吗？他们一直在恐吓\n\
这一带的村庄。一个叫凯撒鲁斯的家伙是他们的首领。\n\
如果你能解决他们，也许村民会给你一些报酬。"
