import cmd
import textwrap
import sys
import os
import data, enemies

screen_width = 100

def title_screen_selection():
    option = int(input("> "))
    if option == (1):
        os.system("cls")
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
    os.system("cls")
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
        if option == (1):
            enemy = enemies.Imp()
            data.combat(my_play, enemy)
            input("\n按 Enter 继续...")
            os.system("cls")
        elif option == (2):
            os.system("cls")
            data.show_stats(my_play)
            input("\n按 Enter 继续...")
            os.system("cls")
        elif option == (3):
            pass
        else:
            pass

if __name__ == "__main__":
    title_screen()