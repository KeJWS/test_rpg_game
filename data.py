import random

class Battler():
    def __init__(self, name, level, stats) -> None:
        self.name = name
        self.level = level
        self.stats = stats

class Player(Battler):
    def __init__(self, name) -> None:
        stats = {
            "hp": 100,
            "mp": 10,
            "atk": 20,
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
            "hp": 100,
            "mp": 5,
            "atk": 15,
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
    while player.stats["hp"] > 0 and enemy.stats["hp"] > 0:
        print("-----------------------")
        decision = random.choice(["y", "n"])
        print(f"自动决策: {decision}")
        if decision == "y":
            print(f"{player.name}趁机进攻！")
            take_dmg(player, enemy)
        elif decision == "n":
            print(f"{enemy.name}趁机进攻！")
            take_dmg(enemy, player)
        else:
            pass

        if player.stats["hp"] <= 0 or enemy.stats["hp"] <= 0:
            print("战斗结束！")
            break
