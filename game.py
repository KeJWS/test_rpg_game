import sys
import random

import combat, enemies, text, inventory, player, items, events, skills

from test.clear_screen import clear_screen, enter_clear_screen
from test.save_system import save_game, get_save_list, delete_save, load_game

import test.fx

#### 标题屏幕 #####
def title_screen_selections():
    text.title_screen()
    option = input("> ")
    while option not in ["1", "2", "3"]:
        print("请输入有效命令")
        option = input("> ")
    if option == "1":
        clear_screen()
        play()
    elif option == "2":
        text.help_menu()
    elif option == "3":
        sys.exit()

##### 库存菜单 #####
def inventory_selections(player):
    option = input("> ")
    while option.lower() != "q":
        match option.lower():
            case "u":
                player.use_item(player.inventory.use_item())
            case "d":
                player.inventory.drop_item()
            case "e":
                player.equip_item(player.inventory.equip_item())
            case _:
                pass
        enter_clear_screen()
        text.inventory_menu()
        option = input("> ")
    enter_clear_screen()

def handle_save_menu(player):
    """处理存档菜单逻辑，返回可能更新的玩家对象"""
    save_option = int(input("> "))
    match save_option:
        case 1:
            save_name = input("输入存档名 (留空使用默认名称): ").strip()
            save_name = save_name if save_name else None
            save_metadata = save_game(player, save_name)
            print(f"游戏已保存: {save_metadata['name']}")
        case 2:
            saves = get_save_list()
            if not saves:
                print("没有可用存档。")
                return player
            text.display_save_list(saves)
            save_index = int(input("> "))
            if 1 <= save_index <= len(saves):
                loaded_player = load_game(saves[save_index-1]["name"])
                if loaded_player:
                    print(f"游戏已加载: {loaded_player.name} (等级 {loaded_player.level})")
                    return loaded_player
        case 3:
            saves = get_save_list()
            if not saves:
                print("没有可删除的存档")
                return player
            text.display_save_list(saves)
            save_index = int(input("> "))
            if 1 <= save_index <= len(saves):
                if delete_save(saves[save_index-1]["name"]):
                    print("存档已删除")
    return player

def mystical_crystal(my_player):
    cost = 50 * my_player.level

    print("\n" + "="*34)
    print(f"一个神秘的魔法水晶, 可以完全恢复,\n但需要花费: {cost}G")
    print("-"*34)

    if my_player.money < cost:
        print("金币不足!")
        return

    confirm = input("确认抚摸吗? (y/n): ").lower()
    if confirm == 'y':
        my_player.money -= cost
        combat.fully_heal(my_player)
        combat.fully_recover_mp(my_player)
    else:
        print("已取消。")

##### 初始化函数#####
def play():
    # 玩家实例
    my_player = player.Player("Test Player")

    give_initial_items(my_player)

    while my_player.alive:
        text.play_menu()
        option = input("> ")
        match option:
            case "1":
                clear_screen()
                generate_event(my_player)
                enter_clear_screen()
            case "2":
                clear_screen()
                text.show_stats(my_player)
                enter_clear_screen()
            case "3":
                clear_screen()
                my_player.assign_aptitude_points()
                enter_clear_screen()
            case "4":
                clear_screen()
                text.inventory_menu()
                my_player.inventory.show_inventory()
                inventory_selections(my_player)
            case "5":
                clear_screen()
                text.save_load_menu()
                handle_save_menu(my_player)
                enter_clear_screen()
            case "6":
                clear_screen()
                text.show_equipment_info(my_player)
                enter_clear_screen()
            case "7":
                clear_screen()
                battle_enemies = combat.create_enemy_group(my_player.level)
                combat.combat(my_player, battle_enemies)
                enter_clear_screen()
            case "8":
                clear_screen()
                my_player.show_quests()
                enter_clear_screen()
            case "9":
                clear_screen()
                mystical_crystal(my_player)
                enter_clear_screen()
            case _:
                clear_screen()
                print("请输入有效命令")

def give_initial_items(my_player):
    print(text.initial_event_text)
    option = str(input("> "))
    while option not in ["1", "2", "3"]:
        option = str(input("> "))
    if option == "1":
        items.rusty_sword.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
    elif option == "2":
        items.broken_dagger.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
    elif option == "3":
        items.old_staff.add_to_inventory_player(my_player.inventory)
        items.old_robes.add_to_inventory_player(my_player.inventory)
        items.grimoire_fireball.add_to_inventory_player(my_player.inventory)
        
    my_player.add_money(100)
    print(test.fx.red("[ 记得在库存 > 装备物品中装备这些物品 ]"))

def generate_event(my_player):
    # 事件概率（%）
    combat_chance = 65
    shop_chance = 120
    heal_chance = 15

    event_list = random.choices(events.event_type_list, weights=(combat_chance, shop_chance, heal_chance), k=1)
    # random.choices 返回一个列表，所以我们需要使用 event_list[0]
    event = random.choice(event_list[0])
    event.effect(my_player)
    if event.is_unique:
        for ev_list in events.event_type_list:
            for e in ev_list:
                if e.name == event.name:
                    for quest in my_player.active_quests:
                        if quest.event == event:
                            quest.complete_quest(my_player)
                    ev_list.remove(event)
                    break

if __name__ == "__main__":
    title_screen_selections()