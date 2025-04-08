import math
import random
import time
import text, skills
from test.fx import dot_loading, typewriter

import test.fx

"""
所有可以进入战斗的实例的父类。
战斗者永远是敌人、玩家的盟友或玩家自己
"""
class Battler():
    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False
        self.is_defending = False

class Enemy(Battler):
    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward

# 所有战斗者都有普通攻击
# 修改 combat.py 中的 normal_attack 函数
def normal_attack(attacker, defender, defender_is_defending=False):
    """普通攻击逻辑（含暴击机制、防御判定）"""
    from test.fx import critical, cyan
    from config import CONFIG
    
    test.fx.battle_log(f"{attacker.name} 发动攻击!", "info")
    dot_loading()

    crit_chance = min(75, attacker.stats["crit"])
    if random.randint(1, 100) <= crit_chance:
        crit_base = attacker.stats["atk"] * 4 + attacker.stats["luk"]
        critical_rates = CONFIG["combat"]["crit_rates"]
        # 将字符串键转换回浮点数
        rates = {float(k): v for k, v in critical_rates.items()}
        rate = random.choices(list(rates.keys()), weights=rates.values())[0]
        print(critical(f"暴击! x{rate}"))
        dmg_variation = CONFIG["combat"]["damage_variation"]
        dmg = round(crit_base * random.uniform(1.0, 1.0 + dmg_variation) * rate)
    else:
        base_dmg = attacker.stats["atk"]*4 - defender.stats["def"]*2 + attacker.stats["luk"] - defender.stats["luk"]
        base_dmg = max(base_dmg, 0)
        dmg_variation = CONFIG["combat"]["damage_variation"]
        dmg = round(base_dmg * random.uniform(1.0 - dmg_variation, 1.0 + dmg_variation))
        
    if defender_is_defending:
        defense_reduction = CONFIG["combat"]["defense_reduction"]
        dmg = round(dmg * defense_reduction)
        typewriter(cyan(f"{defender.name} 正在防御，伤害减半!"))
    if not check_miss(attacker, defender):
        take_dmg(attacker, dmg)

# 受到来自特定来源的伤害
def take_dmg(defender, dmg):
    from test.fx import red, bold, yellow
    """伤害结算与死亡检测"""
    if dmg < 0: dmg = 0
    defender.stats["hp"] -= dmg
    test.fx.battle_log(f"{defender.name} 受到伤害 {yellow(dmg)}", "dmg")
    time.sleep(0.3)
    if defender.stats["hp"] <= 0:
        print(bold(red(f"{defender.name} 被杀死了")))
        defender.alive = False

"""
主战斗循环
"""
# 修改 combat.py 中的 combat 函数
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
            if not battler.alive:
                continue
                
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
                            battlers.remove(target_enemy)
                            enemies.remove(target_enemy)
                    case "s":
                        text.spell_menu(player)
                        option = int(input("> "))
                        if option != 0:
                            target_enemy = select_target(battlers)
                            skill_effect(player.spells[option - 1], player, target_enemy)
                            if target_enemy.alive == False:
                                battlers.remove(target_enemy)
                                enemies.remove(target_enemy)
                    case "d":
                        player.is_defending = True
                        typewriter(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
                    case "e":
                        if try_escape(player): # 逃跑成功，结束战斗
                            return
            else:
                # 使用敌人AI
                action = battler.choose_action(player, enemies)
                
                match action["action"]:
                    case "attack":
                        normal_attack(battler, action["target"], defender_is_defending=player.is_defending)
                    case "ability":
                        skill_effect(action["ability"], battler, action["target"])
                    case "defend":
                        battler.is_defending = True
                        typewriter(f"{battler.name} 进入防御状态!")
                
                if not player.alive:
                    break

        # 重置防御状态
        player.is_defending = False
        for enemy in enemies:
            enemy.is_defending = False

        # 处理buff效果
        for battler in battlers:
            for bd in battler.buffs_and_debuffs:
                bd.check_turns()

    if player.alive:
        for bd in player.buffs_and_debuffs:
            bd.deactivate()
        
        # 计算总经验值
        total_xp = sum(enemy.xp_reward for enemy in enemies if not enemy.alive)
        player.add_exp(total_xp)
        take_a_rest(player)
    else:
        print("\n你被打败了...")

# 从战场上选择某个目标
def select_target(targets):
    text.select_objective(targets)
    i = int(input("> "))
    if i <= len(targets):
        target = targets[i-1]
        return target

def check_miss(attacker, defender):
    chance = math.floor(math.sqrt(max(0, (5 * defender.stats["agi"] - attacker.stats["agi"] * 2))))
    if chance > random.randint(0, 100):
        print(test.fx.red(f"{attacker.name} 攻击失败"))
        return True
    return False

def try_escape(player):
    """逃跑逻辑"""
    escape_chance = min(90, 30 + (player.stats["agi"] * 0.4 + player.stats["luk"] * 0.1))
    if random.randint(1, 100) <= escape_chance:
        print(test.fx.green("逃跑成功!"))
        return True
    else:
        print(test.fx.bold_red("逃跑失败!"))
        return False

# 目标恢复一定量的 mp
def recover_mp(target, amount):
    target.stats["mp"] = min(target.stats["hp"] + amount, target.stats["max_mp"])
    print(f"{target.name} 恢复了 {amount}HP")

# 目标恢复一定量的生命值
def heal(target, amount):
    target.stats["hp"] = min(target.stats["hp"] + amount, target.stats["max_hp"])
    print(f"{target.name} 治愈了 {amount}HP")

# 激活特定技能的效果
def skill_effect(skill, caster, target):
    if isinstance(skill, skills.Simple_offensive_spell):
        amount = skill.effect(caster, target)
        take_dmg(target, amount)
    elif isinstance(skill, skills.Simple_heal_spell):
        amount = skill.effect(caster, target)
        heal(caster, amount)
    elif isinstance(skill, skills.Buff_debuff_spell):
        skill.effect(caster, caster)

# 完全治愈目标（调试）
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
