import cmd
import textwrap
import sys
import os
import random
import combat, enemies, text, inventory, player, items
from test.clear_screen import clear_screen, enter_clear_screen

def title_screen_selection():
    text.title_screen()
    option = int(input("> "))
    if option == 1:
        clear_screen()
        play()
    elif option == 2:
        text.help_menu()
    elif option == 3:
        sys.exit()
    while option not in [1,2,3]:
        print("请输入有效字符")
        option = int(input("> "))

def inventory_selections(player):
    option = input("> ")
    while option.lower() != "q":
        if option.lower() == "s":
            player.money += player.inventory.sell_item()
        elif option.lower() == "d":
            player.inventory.drop_item()
        elif option.lower() == "e":
            player.equip_item(player.inventory.equip_item())
        else:
            pass
        option = input("> ")

def play():
    my_player = player.Player("Test Player")
    potions = inventory.Item("生命药水", "a", 10, 10)
    potions.add_to_inventory(my_player.inventory)
    items.debug_sword.add_to_inventory(my_player.inventory)
    items.dagger.add_to_inventory(my_player.inventory)

    while my_player.alive:
        text.play_menu()
        option = int(input("> "))
        match option:
            case 1:
                random_chosen_enemy = random.randint(1, 2)
                if random_chosen_enemy == 1:
                    enemy = enemies.Imp()
                elif random_chosen_enemy == 2:
                    enemy = enemies.Golem()
                combat.combat(my_player, enemy)
                enter_clear_screen()
            case 2:
                clear_screen()
                text.show_stats(my_player)
                enter_clear_screen()
            case 3:
                clear_screen()
                my_player.assign_aptitude_points()
                enter_clear_screen()
            case 4:
                clear_screen()
                text.inventory_menu()
                my_player.inventory.show_inventory()
                inventory_selections(my_player)
            case 5:
                my_player.auto_mode = not my_player.auto_mode
                combat.fully_heal(my_player)
            case _:
                pass

if __name__ == "__main__":
    title_screen_selection()