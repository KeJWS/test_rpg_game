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

    # 受到来自特定来源的伤害
    def take_dmg(self, dmg):
        from test.fx import red, bold, yellow
        """伤害结算与死亡检测"""
        if dmg < 0: dmg = 0
        self.stats["hp"] -= dmg
        test.fx.battle_log(f"{self.name} 受到伤害 {yellow(dmg)}", "dmg")
        time.sleep(0.3)
        if self.stats["hp"] <= 0:
            print(bold(red(f"{self.name} 被杀死了")))
            self.alive = False

    # 所有战斗者都有普通攻击
    def normal_attack(self, defender, defender_is_defending=False):
        """普通攻击逻辑（含暴击机制、防御判定）"""
        from test.fx import critical, cyan
        test.fx.battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        crit_chance = min(75, self.stats["crit"])
        # 检查暴击
        if random.randint(1, 100) <= crit_chance:
            crit_base = self.stats["atk"] * 4 + self.stats["luk"]
            critical_rates = { # 暴击倍率 : 概率
                1.5: 50,
                2.0: 30,
                2.5: 15,
                3.0: 5
                }
            rate = random.choices(list(critical_rates.keys()), weights=critical_rates.values())[0]
            print(critical(f"暴击! x{rate}"))
            dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)
            test.fx.battle_log(f"{self.name} 对 {defender.name} 造成了 {dmg} 点暴击伤害", "crit")
        else:
            base_dmg = self.stats["atk"]*4 - defender.stats["def"]*2 + self.stats["luk"] - defender.stats["luk"]
            base_dmg = max(base_dmg, 0)
            dmg = round(base_dmg * random.uniform(0.8, 1.2)) # 伤害浮动：±20%
        if defender_is_defending:
            dmg = round(dmg * 0.5)
            typewriter(cyan(f"{defender.name} 正在防御，伤害减半!"))
        # 检查攻击失败
        if not check_miss(self, defender):
            defender.take_dmg(dmg)

    # 目标恢复一定量的 mp
    def recover_mp(self, amount):
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        print(f"{self.name} 恢复了 {amount}MP")

    # 目标恢复一定量的生命值
    def heal(self, amount):
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        print(f"{self.name} 治愈了 {amount}HP")

class Enemy(Battler):
    def __init__(self, name, stats, xp_reward, gold_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward

"""
主战斗循环
"""
def combat(player, enemies):
    """主战斗流程控制"""
    # 所有战斗者都被插入到战斗者列表中，并按速度（回合顺序）排序
    battlers = define_battlers(player, enemies)

    print("---------------------------------------")
    for enemy in enemies:
        print(f"野生的 {enemy.name} 出现了!")
    # 只要玩家还活着，并且还有敌人需要击败，战斗就会继续
    while player.alive and len(enemies) > 0:
        # 战士应该根据速度变化进行更新（增益/减益）
        battlers = define_battlers(player, enemies)
        for battler in battlers:
            # 如果战斗者是盟友，则用户可以控制其行动
            if battler.is_ally:
                text.combat_menu(player, enemies)
                decision = input("> ").lower()
                while decision not in ["a", "d", "c", "s", "e"]:
                    decision = input("> ").lower()
                match decision:
                    case "a":
                        target_enemy = select_target(enemies)
                        battler.normal_attack(target_enemy)
                        check_if_dead(target_enemy, enemies, battlers)
                    case "s":
                        text.spell_menu(player)
                        option = int(input("> "))
                        while option not in range(len(player.spells)+1):
                            print("请输入有效的数字")
                            option = int(input("> "))
                        if option != 0:
                            spell_chosen = player.spells[option - 1]
                            if spell_chosen.is_targeted:
                                target = select_target(battlers)
                                spell_chosen.effect(player, target)
                                check_if_dead(target, enemies, battlers)
                            else:
                                spell_chosen.effect(player, player)
                    case "d":
                        player.is_defending = True
                        typewriter(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
                    case "e":
                        if try_escape(player): # 逃跑成功，结束战斗
                            return
                        check_if_dead(player, enemies, battlers)
            else:
                # 目前，敌人将对玩家进行正常攻击。
                # 这可以扩展为功能性 AI
                battler.normal_attack(player, defender_is_defending=player.is_defending)

        player.is_defending = False

        # 一轮已过
        # 检查增益和减益效果的回合
        for battler in battlers:
            check_turns_buffs_and_debuffs(battler, False)

    if player.alive:
        # 停用所有现有的增益效果和减益效果
        check_turns_buffs_and_debuffs(player, True)
        # 为玩家添加经验
        player.add_exp(enemy.xp_reward)
        take_a_rest(player)

# 返回按速度（回合顺序）排序的战斗者列表
# 当从“玩家”更改为“盟友”时，应将其更改为
def define_battlers(player, enemies):
    battlers = enemies.copy()
    battlers.append(player)
    battlers.sort(key=lambda b: b.stats["agi"], reverse=True)
    return battlers

# 从战场上选择某个目标
def select_target(targets):
    text.select_objective(targets)
    i = int(input("> "))
    while i not in range(len(targets)+1):
        print()
        i = int(input("> "))
    target = targets[i-1]
    return target

# 如果攻击失败则返回 True，否则返回 False
def check_miss(attacker, defender):
    chance = math.floor(math.sqrt(max(0, (5 * defender.stats["agi"] - attacker.stats["agi"] * 2))))
    if chance > random.randint(0, 100):
        print(test.fx.red(f"{attacker.name} 的攻击被 {defender.name} 躲开了"))
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

# 检查增益和减益效果是否仍应处于活动状态
# 如果 deactivate = True，它们将立即停用
def check_turns_buffs_and_debuffs(target, deactivate):
    if deactivate:
        for bd in target.buffs_and_debuffs:
            bd.deactivate()
    else:
        for bd in target.buffs_and_debuffs:
            bd.check_turns()

# 检查战斗者是否死亡并将其从适当的列表中删除
def check_if_dead(target, enemies, battlers):
    if target.is_ally:
        # 这里应该将其从“盟友”列表中删除
        # 玩家暂时不使用此功能
        pass
    else:
        if target.alive == False:
            battlers.remove(target)
            enemies.remove(target)

# 完全治愈目标
def fully_heal(target):
    """HP 恢复相关函数"""
    target.stats["hp"] = target.stats["max_hp"]
    print(f"{target.name} 的生命完全恢复了!")

def fully_recover_mp(target):
    target.stats["mp"] = target.stats["max_mp"]
    print(f"{target.name} 的魔法完全恢复了!")

def take_a_rest(player):
    """战斗后休息恢复"""
    player.stats["hp"] = min(player.stats["max_hp"], player.stats["hp"] + int(player.stats["max_hp"] * 0.25))
    player.stats["mp"] = min(player.stats["max_mp"], player.stats["mp"] + int(player.stats["max_mp"] * 0.25))
    print("\n稍作休整, 恢复了一部分生命值和魔法, 准备迎接下一个怪物!")
