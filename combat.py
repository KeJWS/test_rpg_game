import random
import text, skills

class Battler():

    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True

class Enemy(Battler):

    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward

def normal_attack(attacker, defender, defender_is_defending=False):
    print(f"{attacker.name} 发动攻击!")
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
        base_dmg = attacker.stats["atk"]*4 - defender.stats["def"]*2 + attacker.stats["luk"] - defender.stats["luk"]
        base_dmg = max(base_dmg, 0)
        dmg = round(base_dmg * random.uniform(0.8, 1.2)) # 伤害浮动：±20%
    if defender_is_defending:
        dmg = round(dmg * 0.5)
    take_dmg(attacker, defender, dmg)

def take_dmg(attacker, defender, dmg):
    if dmg < 0: dmg = 0
    defender.stats["hp"] -= dmg
    print(f"{attacker.name} 攻击 {defender.name} 造成伤害 \033[33m{dmg}\033[0m")
    if defender.stats["hp"] <= 0:
        print(f"\033[31m{defender.name} 被杀死了\033[0m")
        defender.alive = False

def combat(player, enemy):
    print("---------------------------------------")
    print(f"野生的 {enemy.name} 出现了!")
    while player.alive and enemy.alive:
        text.combat_menu(player, enemy)
        decision = get_player_decision(player)

        match decision:
            case "a":
                normal_attack(player, enemy)
                if enemy.alive:
                        normal_attack(enemy, player)
            case "s":
                text.spell_menu(player)
                if player.auto_mode:
                    option = random.randint(1, len(player.spells))
                    print(f"自动施放技能: {player.spells[option - 1].name}")
                else:
                    option = int(input("> "))
                if option != 0:
                    skill_effect(player.spells[option - 1], player, enemy)
                    if enemy.alive:
                        normal_attack(enemy, player)
            case "d":
                print(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
                normal_attack(enemy, player, defender_is_defending=True)
            case "q":
                if try_escape(player): # 逃跑成功，结束战斗
                    return
                else:
                    if enemy.alive:
                        normal_attack(enemy, player)
            case _:
                pass

    if player.alive:
            player.add_exp(enemy.xp_reward)
            take_a_rest(player)

def get_player_decision(player):
    """获取玩家的战斗决策"""
    if player.auto_mode:
        decision_weights = []

        has_spells = hasattr(player, "spells") and len(player.spells) > 0
        can_use_spells = has_spells and player.stats["mp"] > player.stats["max_mp"] * 0.3

        decision_weights.append("a")
        decision_weights.append("d")
        if can_use_spells:
            decision_weights.append("s")
        if player.stats["hp"] < player.stats["max_hp"] * 0.3:
            decision_weights.append("q")

        decision = random.choice(decision_weights)
        print(f"自动决策: \033[32m{decision}\033[0m")
        return decision
    return input("选择行动 (a. 攻击 s. 技能 d. 防御 q. 逃跑) ").lower()

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

def skill_effect(skill, attacker, defender):
    if type(skill) == skills.Simple_offensive_spell:
        dmg = skill.effect(attacker, defender)
        take_dmg(attacker, defender, dmg)

def fully_heal(target):
    target.stats["hp"] = target.stats["max_hp"]
    target.stats["mp"] = target.stats["max_mp"]
    print(f"{target.name} 完全恢复了!")

def take_a_rest(player):
    player.stats["hp"] = min(player.stats["max_hp"], player.stats["hp"] + int(player.stats["max_hp"] * 0.25))
    player.stats["mp"] = min(player.stats["max_mp"], player.stats["mp"] + int(player.stats["max_mp"] * 0.25))
    print("\n稍作休整, 恢复了一部分生命值和魔法, 准备迎接下一个怪物!")
