
import time, sys

BOLD_UNDERLINED = "\033[1:4m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLO = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
CYAN = "\033[36m"
END = "\033[0m"

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def red(text): return color(text, "31")
def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def blue(text): return color(text, "34")
def magenta(text): return color(text, "35")
def cyan(text): return color(text, "36")
def bold(text): return color(text, "1")
def blink(text): return color(text, "5")
def underlined(text): return color(text, "4")

def critical(text): return color(text, "1;33")
def dmg(text): return color(text, "31")
def heal_fx(text): return color(text, "32")
def log_title(text): return color(text, "1;36")

def bold_yellow(text): return color(text, "1;33")
def bold_red(text): return color(text, "1;31")
def bold_green(text): return color(text, "1;32")

def bright_cyan(text): return color(text, "46")

def log(msg):
    print(f"{log_title('[LOG]')} {msg}")

def typewriter(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def dot_loading(text="正在行动", dots=3, delay=0.3):
    print(text, end="", flush=True)
    for _ in range(dots):
        time.sleep(delay)
        print(".", end="", flush=True)
    print()


def slow_print(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def divider():
    print(color("-" * 40, "90"))

def battle_log(message, style=""):
    match style:
        case "dmg": slow_print(yellow(message))
        case "crit": slow_print(bold_yellow(message))
        case "heal": slow_print(green(message))
        case "death": slow_print(bold_red(message))
        case "info": slow_print(cyan(message))
        case "magic": slow_print(blue(message))
        case _: slow_print(message)
