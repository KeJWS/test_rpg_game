import random

class Battler():

    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True

class Player(Battler):

    def __init__(self, name) -> None:
        stats = {
            "hp": 200,
            "mp": 10,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
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
    dmg = round(attacker.stats["atk"]*4 - defender.stats["def"]*2)
    if dmg < 0: dmg = 0
    if defending:
        dmg = int(dmg * 0.5) # 如果处于防御状态，伤害减少50%
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
    player.xp += exp
    while(player.xp >= player.xp_to_next_level):
        player.xp -= player.xp_to_next_level
        player.level += 1
        player.xp_to_next_level = round(player.xp_to_next_level * 1.5)
        for stat in player.stats:
            player.stats[stat] += 2
        print(f"\033[33m升级！您现在的等级是: {player.level}\033[0m")

def show_stats(player):
    stats_template = (
        f"----------------------------------\n"
        f"  STATS\n"
        f"----------------------------------\n"
        f"      LV: {player.level}        EXP: {player.xp}/{player.xp_to_next_level}\n"
        f"      \033[31mHP: {player.stats['hp']}\033[0m       \033[34mMP: {player.stats['mp']}\033[0m\n"
        f"      ATK: {player.stats['atk']}        DEF: {player.stats['def']}\n"
        f"      MAT: {player.stats['mat']}        MDF: {player.stats['mdf']}\n"
        f"      AGI: {player.stats['agi']}        CRT: {player.stats['crit']}\n"
        f"----------------------------------\n"
        f"  APTITUDES\n"
        f"----------------------------------\n"
        f"      STR: {player.aptitudes['str']}        DEX: {player.aptitudes['dex']}\n"
        f"      INT: {player.aptitudes['int']}        WIS: {player.aptitudes['wis']}\n"
        f"      CONST: {player.aptitudes['const']}\n"
        f"----------------------------------\n"
    )
    print(stats_template)
