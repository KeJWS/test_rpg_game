import random
import text, inventory
from test.constants import EXPERIENCE_RATE

class Battler():

    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True

class Player(Battler):

    def __init__(self, name) -> None:
        stats = {
            "max_hp": 500,
            "hp": 500,
            "max_mp": 10,
            "mp": 10,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10, # 幸运影响伤害和经验获得量
            "crit": 5
        }

        super().__init__(name, stats)

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50
        self.aptitudes = {
            "str": 5,
            "dex": 5,
            "int": 5,
            "wis": 5,
            "const": 5
        }
        self.aptitude_points = 5
        self.auto_mode = True
        self.inventory = inventory.Inventory()

class Enemy(Battler):

    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward

def take_dmg(attacker, defender, defending=False):
    if attacker.stats["crit"] > random.randint(1, 100):
        crit_base = attacker.stats["atk"] * 4 + attacker.stats["luk"]
        critical_rates = { # 暴击倍率 : 概率
            1.5: 50,
            2.0: 30,
            2.5: 15,
            3.0: 5
            }
        rate = random.choices(list(critical_rates.keys()), weights=critical_rates.values())[0]
        print(f'\033[1;33m暴击！x{rate}\033[0m')
        dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)

    else:
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
        if player.auto_mode == True:
            decision = random.choice(["a", "d"])
            print(f"自动决策: \033[32m{decision}\033[0m")
        elif player.auto_mode == False:
            decision = input("Attack or defense? (a/d): ").lower()
        if decision == "a":
            print(f"{player.name} 趁机进攻！")
            take_dmg(player, enemy)
            if enemy.alive == True:
                print(f"{enemy.name} 趁机进攻！")
                take_dmg(enemy, player)
        elif decision == "d":
            print(f"{player.name} 选择防御, 本回合受到的伤害将减少50%！")
            print(f"{enemy.name} 趁机进攻！")
            take_dmg(enemy, player, defending=True)
        else:
            pass

    if player.alive:
            add_exp(player, enemy.xp_reward)
            take_a_rest(player)

def add_exp(player, exp):
    exp_value = (exp + player.stats["luk"]) * EXPERIENCE_RATE
    player.xp += exp_value
    print(f"获得了 {exp_value}xp")
    while(player.xp >= player.xp_to_next_level):
        player.xp -= player.xp_to_next_level
        player.level += 1
        player.xp_to_next_level = round(player.xp_to_next_level * 1.5)
        fully_heal(player)
        for stat in player.stats:
            player.stats[stat] += 1
        print(f"\033[33m升级！您现在的等级是: {player.level}\033[0m")

def assign_aptitude_points(player):
    text.show_aptitudes(player)
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
        "str": {"atk": 3},
        "dex": {"agi": 3, "crit": 1},
        "int": {"mat": 3},
        "wis": {"max_mp": 10},
        "const": {"max_hp": 10}
    }
    updates = aptitude_mapping.get(aptitude, {})
    for stat, value in updates.items():
        player.stats[stat] += value

def fully_heal(target):
    target.stats["hp"] = target.stats["max_hp"]

def take_a_rest(player):
    player.stats["hp"] = min(player.stats["max_hp"], player.stats["hp"] + int(player.stats["max_hp"] * 0.2))
    player.stats["mp"] = min(player.stats["max_mp"], player.stats["mp"] + int(player.stats["max_mp"] * 0.1))
    print("稍作休整, 你恢复了一部分生命值和魔法, 准备迎接下一个怪物!")
