import cmd
import textwrap
import sys
import os
import data, enemies
from test.clear_screen import clear_screen, enter_clear_screen

def title_screen_selection():
    option = int(input("> "))
    if option == 1:
        clear_screen()
        play()
    elif option == 2:
        help_menu()
    elif option == 3:
        sys.exit()
    while option not in [1,2,3]:
        print("请输入有效字符")
        option = int(input("> "))

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
    title_screen_selection()

def help_menu():
    clear_screen()
    print("")

def play():
    my_play = data.Player("Test Player")
    display_content = (
        "--------------------------------\n"
        "   1 - Battle\n"
        "   2 - See stats\n"
        "   3 - Assign aptitude points   \n"
        "--------------------------------\n"
    )

    while True:
        print(display_content)
        option = int(input("> "))
        if option == 1:
            enemy = enemies.Imp()
            data.combat(my_play, enemy)
            enter_clear_screen()
        elif option == 2:
            clear_screen()
            data.show_stats(my_play)
            enter_clear_screen()
        elif option == 3:
            clear_screen()
            data.assign_aptitude_points(my_play)
            enter_clear_screen()
        else:
            pass

if __name__ == "__main__":
    title_screen()