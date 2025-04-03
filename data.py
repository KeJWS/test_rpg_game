import random

class Battler():
    def __init__(self, name, level, stats) -> None:
        self.name = name
        self.level = level
        self.stats = stats

class Player(Battler):
    def __init__(self, name) -> None:
        stats = {
            "hp": 10,
            "mp": 10,
            "atk": 10,
            "def": 10,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "crit": 10
        }

        super().__init__(name, 1, stats)

        self.xp = 0
        self.xp_to_next_level = 25
        self.aptitudes = {
            "str": 5,
            "dex": 5,
            "wis": 5,
            "const": 5
        }

class Imp(Battler):
    def __init__(self) -> None:
        stats = {
            "hp": 200,
            "mp": 5,
            "atk": 5,
            "def": 5,
            "mat": 5,
            "mdf": 5,
            "agi": 5,
            "crit": 5
        }
        super().__init__("Imp", 1, stats)

def take_dmg(attacker, defender):
    dmg = attacker.stats["atk"] - defender.stats["def"]
    if dmg < 0: dmg = 0
    defender.stats["hp"] -= dmg
    if defender.stats["hp"] <= 0:
        print(f"\033[31m{defender.name} 被击杀了。\033[0m")
    else:
        print(f"{defender.name} 受到 \033[33m{dmg}\033[0m 点伤害！")

def combat(player, enemy):
    while True:
        print()
        cmd = input("攻击? y/n: ").lower()
        if "y" in cmd:
            print(f"{player.name}趁机进攻！")
            take_dmg(player, enemy)
        elif "n" in cmd:
            print(f"{enemy.name}趁机进攻！")
            take_dmg(enemy, player)
        else:
            pass
