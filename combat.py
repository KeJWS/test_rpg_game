import random

class Battler():

    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True

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
    print(f"野生的 {enemy.name} 出现了!")
    while player.alive and enemy.alive:
        print("\n-----------------------")
        decision = get_player_decision(player)

        match decision:
            case "a":
                print(f"{player.name} 趁机进攻!")
                take_dmg(player, enemy)
                handle_enemy_attack(player, enemy)
            case "d":
                print(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
                handle_enemy_attack(player, enemy)
            case "q":
                if try_escape(player): # 逃跑成功，结束战斗
                    return
                else:
                    print(f"{enemy.name} 乘胜追击!")
                    take_dmg(enemy, player)
            case _:
                pass

    if player.alive:
            player.add_exp(enemy.xp_reward)
            take_a_rest(player)

def get_player_decision(player):
    """获取玩家的战斗决策"""
    if player.auto_mode:
        if player.stats["hp"] < player.stats["max_hp"] * 0.3 and random.random() < 0.5:
            decision = "q"
        else:
            decision = random.choice(["a", "d"])
        print(f"自动决策: \033[32m{decision}\033[0m")
        return decision
    return input("选择行动 (a. 攻击 d. 防御 q. 逃跑) ").lower()

def handle_enemy_attack(player, enemy):
    """处理敌人攻击逻辑"""
    if enemy.alive:
        print(f"{enemy.name} 趁势回击!")
        take_dmg(enemy, player)

def try_escape(player):
    """尝试逃跑, 计算成功概率"""
    escape_chance = min(90, max(10, player.stats["agi"] + player.stats["luk"]))
    if random.randint(1, 100) <= escape_chance:
        print("\033[32m逃跑成功!\033[0m")
        return True
    else:
        print("\033[31m逃跑失败!\033[0m")
        return False

def heal(target, amount):
    if target.stats["hp"] + amount > target.stats["max_hp"]:
        target.stats["hp"] = target.stats["max_hp"]
        target.stats["hp"] += amount

def fully_heal(target):
    target.stats["hp"] = target.stats["max_hp"]

def take_a_rest(player):
    player.stats["hp"] = min(player.stats["max_hp"], player.stats["hp"] + int(player.stats["max_hp"] * 0.2))
    player.stats["mp"] = min(player.stats["max_mp"], player.stats["mp"] + int(player.stats["max_mp"] * 0.1))
    print("\n稍作休整, 恢复了一部分生命值和魔法, 准备迎接下一个怪物!")
