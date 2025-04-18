import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def enter_clear_screen():
    input("\n按 Enter 继续...")
    os.system('cls' if os.name == 'nt' else 'clear')

def screen_wrapped(func):
    def wrapper(*args, **kwargs):
        clear_screen()
        result = func(*args, **kwargs)
        enter_clear_screen()
        return result
    return wrapper
