import random
import text
from test.constants import EXPERIENCE_RATE

class Battler():

    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True

class Player(Battler):

    def __init__(self, name) -> None:
        stats = {
            "max_hp": 200,
            "hp": 200,
            "max_mp": 10,
            "mp": 10,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10,
            "crit": 10
        }

        super().__init__(name, stats)

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 25
        self.aptitudes = {
            "str": 5,
            "dex": 5,
            "int": 5,
            "wis": 5,
            "const": 5
        }
        self.aptitude_points = 5

class Enemy(Battler):

    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward

def take_dmg(attacker, defender, defending=False):
    base_dmg = round(attacker.stats["atk"]*4 - defender.stats["def"]*2 + attacker.stats["luk"] - defender.stats["luk"])
    if base_dmg < 0: base_dmg = 0

    dmg = round(base_dmg * random.uniform(0.8, 1.2)) # 伤害浮动：±20%

    if defending:
        dmg = int(dmg * 0.5) # 防御状态，伤害减少50%
    defender.stats["hp"] -= dmg
    print(f"{defender.name} 受到 \033[33m{dmg}\033[0m 点伤害！")
    if defender.stats["hp"] <= 0:
        print(f"\033[31m{defender.name} 被击杀了。\033[0m")
        defender.alive = False
    else:
        print(f"{defender.name} 还剩 \033[31m{defender.stats["hp"]}\033[0m 血量。")

def combat(player, enemy):
    print("-----------------------")
    print(f"野生的 {enemy.name} 出现了！")
    while player.alive and enemy.alive:
        print("\n-----------------------")
        decision = random.choice(["attack", "defend"])
        print(f"自动决策: \033[32m{decision}\033[0m")
        if decision == "attack":
            print(f"{player.name}趁机进攻！")
            take_dmg(player, enemy)
        elif decision == "defend":
            print(f"{player.name} 选择防御, 本回合受到的伤害将减少50%！")
            print(f"{enemy.name}趁机进攻！")
            take_dmg(enemy, player, defending=True)
        else:
            pass

    if player.alive:
            add_exp(player, enemy.xp_reward)

def add_exp(player, exp):
    player.xp += (exp + player.stats["luk"]) * EXPERIENCE_RATE
    while(player.xp >= player.xp_to_next_level):
        player.xp -= player.xp_to_next_level
        player.level += 1
        player.xp_to_next_level = round(player.xp_to_next_level * 1.5)
        player.stats["hp"] = player.stats["max_hp"]
        for stat in player.stats:
            player.stats[stat] += 1
        print(f"\033[33m升级！您现在的等级是: {player.level}\033[0m")

def show_stats(player):
    stats_template = (
        f"----------------------------------\n"
        f"  STATS\n"
        f"----------------------------------\n"
        f"      LV: {player.level}        EXP: {player.xp}/{player.xp_to_next_level}\n"
        f"      \033[31mHP: {player.stats['hp']}/{player.stats['max_hp']}\033[0m    \033[34mMP: {player.stats['mp']}/{player.stats['max_mp']}\033[0m\n"
        f"      ATK: {player.stats['atk']}        DEF: {player.stats['def']}\n"
        f"      MAT: {player.stats['mat']}        MDF: {player.stats['mdf']}\n"
        f"      AGI: {player.stats['agi']}        LUK: {player.stats['luk']}\n"
        f"      CRT: {player.stats['crit']}\n"
        f"----------------------------------\n"
        f"  APTITUDES\n"
        f"----------------------------------\n"
        f"      STR: {player.aptitudes['str']}        DEX: {player.aptitudes['dex']}\n"
        f"      INT: {player.aptitudes['int']}        WIS: {player.aptitudes['wis']}\n"
        f"      CONST: {player.aptitudes['const']}\n"
        f"----------------------------------\n"
    )
    print(stats_template)

def show_aptitudes(player):
    display_aptitudes = (
        f"----------------------------------\n"
        f"  POINTS: {player.aptitude_points}\n"
        f"  SELECT AN APTITUDE\n"
        f"----------------------------------\n"
        f"      1 - STR (Current: {player.aptitudes['str']})\n"
        f"      2 - DEX (Current: {player.aptitudes['dex']})\n"
        f"      3 - INT (Current: {player.aptitudes['int']})\n"
        f"      4 - WIS (Current: {player.aptitudes['wis']})\n"
        f"      5 - CONST (Current: {player.aptitudes['const']})\n"
        f"      0 - Quit menu\n"
        f"----------------------------------\n"
    )
    print(display_aptitudes)

def assign_aptitude_points(player):
    show_aptitudes(player)
    option = int(input("> "))
    options_dictionary = {
        1: "str",
        2: "dex",
        3: "int",
        4: "wis",
        5: "const"
    }
    while option != 0:
        if option in range(1, 6):
            if player.aptitude_points >= 1:
                aptitude_to_assign = options_dictionary[option]
                player.aptitudes[aptitude_to_assign] += 1
                print(f"{aptitude_to_assign} 增加到了 {player.aptitudes[aptitude_to_assign]}")
                update_stats_to_aptitudes(player, aptitude_to_assign)
                player.aptitude_points -= 1
            else:
                print("没有足够的能力点!")
        else:
            print("不是有效字符！")
        option = int(input("> "))

def update_stats_to_aptitudes(player, aptitude):
    aptitude_mapping = {
        "str": {"atk": 2},
        "dex": {"agi": 1, "crit": 1},
        "int": {"mat": 2},
        "wis": {"max_mp": 5},
        "const": {"max_hp": 5}
    }
    updates = aptitude_mapping.get(aptitude, {})
    for stat, value in updates.items():
        player.stats[stat] += value
