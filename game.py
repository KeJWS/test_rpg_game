import cmd
import textwrap
import sys
import os
import random
import data, enemies, text
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

def play():
    my_play = data.Player("Test Player")

    while my_play.alive:
        text.play_menu()
        option = int(input("> "))
        match option:
            case 1:
                random_chosen_enemy = random.randint(1, 2)
                if random_chosen_enemy == 1:
                    enemy = enemies.Imp()
                elif random_chosen_enemy == 2:
                    enemy = enemies.Golem()
                data.combat(my_play, enemy)
                enter_clear_screen()
            case 2:
                clear_screen()
                text.show_stats(my_play)
                enter_clear_screen()
            case 3:
                clear_screen()
                data.assign_aptitude_points(my_play)
                enter_clear_screen()
            case 4:
                data.fully_heal(my_play)
            case _:
                pass

if __name__ == "__main__":
    title_screen_selection()