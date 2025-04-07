import math
import random
import text, skills

class Battler():
    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False

class Enemy(Battler):
    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward

def normal_attack(attacker, defender, defender_is_defending=False):
    """普通攻击逻辑（含暴击机制、防御判定）"""
    print(f"{attacker.name} 发动攻击!")
    crit_chance = min(75, attacker.stats["crit"])
    if random.randint(1, 100) <= crit_chance:
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
    if not check_miss(attacker, defender):
        take_dmg(attacker, defender, dmg)

def take_dmg(attacker, defender, dmg):
    """伤害结算与死亡检测"""
    if dmg < 0: dmg = 0
    defender.stats["hp"] -= dmg
    print(f"{attacker.name} 攻击 {defender.name} 造成伤害 \033[33m{dmg}\033[0m")
    if defender.stats["hp"] <= 0:
        print(f"\033[31m{defender.name} 被杀死了\033[0m")
        defender.alive = False

def combat(player, enemies):
    """主战斗流程控制"""
    battlers = enemies.copy()
    battlers.append(player)
    battlers.sort(key=lambda b: b.stats["agi"], reverse=True)
    print("---------------------------------------")
    for enemy in enemies:
        print(f"野生的 {enemy.name} 出现了!")
    while player.alive and len(enemies) > 0:
        for battler in battlers:
            if battler.is_ally:
                text.combat_menu(player, enemies)
                decision = input("> ").lower()
                while decision not in ["a", "d", "c", "s", "e"]:
                    decision = input("> ").lower()
                match decision:
                    case "a":
                        target_enemy = select_target(enemies)
                        normal_attack(player, target_enemy)
                        if target_enemy.alive == False:
                            battlers.remove(enemy)
                            enemies.remove(enemy)
                    case "s":
                        text.spell_menu(player)
                        option = int(input("> "))
                        if option != 0:
                            target_enemy = select_target(battlers)
                            skill_effect(player.spells[option - 1], player, target_enemy)
                            if target_enemy.alive == False:
                                battlers.remove(enemy)
                                enemies.remove(enemy)
                    case "d":
                        print(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
                        if target_enemy.alive == False:
                            battlers.remove(enemy)
                            enemies.remove(enemy)
                    case "e":
                        if try_escape(player): # 逃跑成功，结束战斗
                            return
            else:
                normal_attack(battler, player)

        for bd in player.buffs_and_debuffs:
            bd.check_turns()
        for bd in enemy.buffs_and_debuffs:
            bd.check_turns()

    if player.alive:
        for bd in player.buffs_and_debuffs:
            bd.deactivate()
        player.add_exp(enemy.xp_reward)
        take_a_rest(player)

def select_target(targets):
    text.select_objective(targets)
    i = int(input("> "))
    if i <= len(targets):
        target = targets[i-1]
        return target

def check_miss(attacker, defender):
    chance = math.floor(math.sqrt(max(0, (5 * defender.stats["agi"] - attacker.stats["agi"] * 2))))
    if chance > random.randint(0, 100):
        print(f"\033[31m{attacker.name} 攻击失败\033[0m")
        return True
    return False

def get_player_decision(player):
    """获取行动指令（含自动模式 AI 决策）"""
    if player.auto_mode:
        decision_weights = []
        decision_weights.append("a")
        decision_weights.append("d")
        if player.stats["hp"] < player.stats["max_hp"] * 0.3:
            decision_weights.append("q")

        decision = random.choice(decision_weights)
        print(f"自动决策: \033[32m{decision}\033[0m")
        return decision
    return input("选择行动 (a. 攻击 s. 技能 d. 防御 q. 逃跑) ").lower()

def try_escape(player):
    """逃跑逻辑"""
    escape_chance = min(90, 30 + (player.stats["agi"] * 0.4 + player.stats["luk"] * 0.1))
    if random.randint(1, 100) <= escape_chance:
        print("\033[32m逃跑成功!\033[0m")
        return True
    else:
        print("\033[31m逃跑失败!\033[0m")
        return False

def recover_mp(target, amount):
    target.stats["mp"] = min(target.stats["hp"] + amount, target.stats["max_mp"])
    print(f"{target.name} 恢复了 {amount}HP")

def heal(target, amount):
    target.stats["hp"] = min(target.stats["hp"] + amount, target.stats["max_hp"])
    print(f"{target.name} 治愈了 {amount}HP")

def skill_effect(skill, caster, target):
    if isinstance(skill, skills.Simple_offensive_spell):
        amount = skill.effect(caster, target)
        take_dmg(caster, target, amount)
    elif isinstance(skill, skills.Simple_heal_spell):
        amount = skill.effect(caster, target)
        heal(caster, amount)
    elif isinstance(skill, skills.Buff_debuff_spell):
        skill.effect(caster, caster)

def fully_heal(target):
    """恢复相关函数"""
    target.stats["hp"] = target.stats["max_hp"]
    target.stats["mp"] = target.stats["max_mp"]
    print(f"{target.name} 完全恢复了!")

def take_a_rest(player):
    """战斗后休息恢复"""
    player.stats["hp"] = min(player.stats["max_hp"], player.stats["hp"] + int(player.stats["max_hp"] * 0.25))
    player.stats["mp"] = min(player.stats["max_mp"], player.stats["mp"] + int(player.stats["max_mp"] * 0.25))
    print("\n稍作休整, 恢复了一部分生命值和魔法, 准备迎接下一个怪物!")
