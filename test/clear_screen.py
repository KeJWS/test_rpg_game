import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def enter_clear_screen():
    input("\n按 Enter 继续...")
    os.system('cls' if os.name == 'nt' else 'clear')
