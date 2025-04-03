import cmd
import textwrap
import sys
import os
import data

screen_width = 100

def title_screen_selection():
    option = int(input("> "))
    if option == (1):
        play()
    elif option == (2):
        help_menu()
    elif option == (3):
        sys.exit()
    while option not in [1,2,3]:
        print("请输入有效命令")
        option = int(input("> "))

def title_screen():
    display_content = (
        "-----------------------\n"
        "\n"
        "-----------------------\n"
        "       1 - Play        \n"
        "       2 - Help        \n"
        "       3 - Quit        \n"
        "-----------------------\n"
    )
    print(display_content)
    title_screen_selection()

def help_menu():
    os.system("clear")
    print("")

def play():
    my_play = data.Player("Test Player")
    my_enemy = data.Imp()
    data.combat(my_play, my_enemy)

if __name__ == "__main__":
    title_screen()