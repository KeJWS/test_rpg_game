import time

def wait(s=0.3):
    time.sleep(s)

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
    print("\r" + " " * 20 + "\r", end="")
