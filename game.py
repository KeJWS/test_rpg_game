import sys
import random

import combat, text, player, items, events
from test.clear_screen import enter_clear_screen, clear_screen
import test.fx
import data.event_text

from save_system import save_game, get_save_list, load_game

### 标题菜单 ###
def title_screen_selections():
    text.title_screen()
    while (option := input("> ")) not in {"1", "2", "3"}:
        print("请输入有效命令")
    match option:
        case "1": clear_screen(); play()
        case "2": text.help_menu()
        case "3":sys.exit()

##### 背包菜单 #####
def inventory_selections(player):
    while (option := input("> ").lower()) != "q":
        match option:
            case "u": clear_screen(); player.use_item(player.inventory.use_item())
            case "d": clear_screen(); player.inventory.drop_item()
            case "e": clear_screen(); player.equip_item(player.inventory.equip_item())
            case "ua": clear_screen(); player.unequip_all()
        enter_clear_screen()
        text.inventory_menu()

### 主游戏循环 ###
def play(p=None):
    from extensions.give_initial_items import give_initial_items, apply_class_bonuses
    if p is None:
        p = player.Player("Test Player")
        print(data.event_text.initial_event_text)
        give_initial_items(p)
        print(test.fx.red("\n[ 记得在库存 > 装备物品中装备这些物品 ]"))
        enter_clear_screen()
    apply_class_bonuses(p)
    enter_clear_screen()
    game_loop(p)

def game_loop(p):
    event_chances = (65, 20, 15)  # 战斗、商店、治疗的概率
    while p.alive:
        text.play_menu()
        match input("> ").lower():
            case "w": clear_screen(); generate_event(p, *event_chances); enter_clear_screen()
            case "s": clear_screen(); text.show_stats(p); enter_clear_screen()
            case "a": clear_screen(); p.assign_aptitude_points(); enter_clear_screen()
            case "i": clear_screen(); text.inventory_menu(); p.inventory.show_inventory(); inventory_selections(p)
            case "lr": clear_screen(); events.life_recovery_crystal(p); enter_clear_screen()
            case "se": clear_screen(); text.show_equipment_info(p); enter_clear_screen()
            case "sk": clear_screen(); text.show_skills(p); enter_clear_screen()
            case "q": clear_screen(); p.show_quests(); enter_clear_screen()
            case "b": clear_screen(); events.random_combat.effect(p); enter_clear_screen()
            case "sg":
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
            case _: clear_screen(); print("请输入有效命令")

    choice = input("是否要转生? (y/n): ")
    if choice.lower() == "y":
        p.rebirth()
        enter_clear_screen()
        play(p)

def generate_event(my_player, combat_chance, shop_chance, heal_chance):
    event_list = random.choices(events.event_type_list, weights=(combat_chance, shop_chance, heal_chance), k=1)
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