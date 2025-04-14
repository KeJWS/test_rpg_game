import math
import random
import time
import text
from test.fx import dot_loading, typewriter, battle_log
from copy import deepcopy
import test.fx as fx

class Battler():
    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False
        self.is_defending = False
        self.spells = []

    def take_dmg(self, dmg):
        from test.fx import red, bold, yellow
        dmg = max(dmg, 0)
        self.stats["hp"] -= dmg
        battle_log(f"{self.name} 受到伤害 {yellow(dmg)}", "dmg")
        time.sleep(0.3)
        # 防御者死亡
        if self.stats["hp"] <= 0:
            print(bold(red(f"{self.name} 被杀死了")))
            self.alive = False

    def normal_attack(self, defender, defender_is_defending=False):
        battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        if self.stats["mat"] > self.stats["atk"]:
            battle_log(f"{self.name} 释放了魔法攻击", "magic")
            dmg = self._calc_magic_damage(defender)
            defender.take_dmg(dmg)
            return dmg

        # 检查是否攻击未命中
        if check_miss(self,defender):
            print(fx.red(f"{self.name} 的攻击被 {defender.name} 躲开了"))
            return 0
        # 检查是否为暴击
        is_crit, crit_suppressed = self._is_critical(defender)
        if is_crit:
            dmg = self._calc_critical_damage(defender)
        elif crit_suppressed:
            battle_log(f"{defender.name} 回避了暴击攻击!", "info")
            dmg = self._calc_normal_damage(defender)
        else:
            dmg = self._calc_normal_damage(defender)

        if defender_is_defending:
            dmg = round(dmg * 0.5)
            typewriter(fx.cyan(f"{defender.name} 正在防御，伤害减半!"))
        defender.take_dmg(dmg)
        return dmg

    def _is_critical(self, defender):
        raw_chance = round(self.stats["crit"] * 0.8 + self.stats["luk"] * 0.2)
        anti_crit = defender.stats.get("anti_crit", 0)
        final_chance = max(0, min(80, raw_chance - anti_crit))

        roll = random.randint(1, 100)
        is_crit = roll <= final_chance
        was_suppressed = raw_chance > final_chance and roll <= raw_chance

        return is_crit, was_suppressed

    def _calc_critical_damage(self, defender):
        crit_base = self.stats["atk"]*3.5 + self.stats["luk"]*1.2
        rate = random.choices([1.5, 2.0, 2.5, 3.0], weights=[50, 30, 17, 3])[0] # 暴击倍率 : 概率
        rate += round(self.stats["crit"]/100, 2)
        print(fx.critical(f"暴击! x{rate}"))
        dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)
        battle_log(f"{self.name} 对 {defender.name} 造成了 {dmg} 点暴击伤害", "crit")
        return dmg

    def _calc_normal_damage(self, defender):
        base = self.stats["atk"]*4 - defender.stats["def"]*2.5
        base += self.stats["luk"] - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.2) * random.uniform(0.8, 1.2)) # 伤害浮动：±20%

    def _calc_magic_damage(self, defender):
        base = self.stats["mat"]*3 - defender.stats["mdf"]*1.7
        base += self.stats["luk"]*1.2 - defender.stats["luk"]
        return round(max(base, self.stats["luk"]*1.5) * random.uniform(0.8, 1.3))

    def recover_mp(self, amount):
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        typewriter(fx.blue(f"{self.name} 恢复了 {amount}MP"))

    def heal(self, amount):
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        typewriter(fx.green(f"{self.name} 治愈了 {amount}HP"))

class Enemy(Battler):
    def __init__(self, name, stats, xp_reward, gold_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.original_stats = stats.copy()

    def clone(self):
        new_stats = self.original_stats.copy()
        return Enemy(self.name, new_stats, self.xp_reward, self.gold_reward)

def combat(my_player, enemies):
    from player import Player
    from skills import enhance_weapon
    # 所有战斗单位（包括玩家和敌人）按速度排序，决定回合顺序
    allies = [my_player]
    battlers = define_battlers(allies, enemies) # 参与战斗的单位（盟友 + 敌人）

    # 统计敌人掉落的经验值和金钱
    enemy_exp = 0
    enemy_money = 0

    print("=================================================")
    for enemy in enemies:
        typewriter(f"野生的 {enemy.name} 出现了!")
        enemy_exp += enemy.xp_reward
        enemy_money += enemy.gold_reward

    # 只要玩家存活且仍有敌人，战斗就会持续
    while my_player.alive and len(enemies) > 0:
        # 由于速度可能因增益/减益效果改变，需要更新战斗顺序
        battlers = define_battlers(allies, enemies)

        # 每个战斗单位轮流行动
        for battler in battlers:
            if not my_player.alive:
                return
            # 玩家回合：选择行动
            if type(battler) == Player:
                text.combat_menu(my_player, allies, enemies)
                cmd = input("> ").lower()
                while cmd not in ["a", "c", "s", "d", "e"]:
                    print("请输入有效指令")
                    cmd = input("> ").lower()
                # 普通攻击
                if "a" in cmd:
                    targeted_enemy = select_target(enemies)
                    battler.normal_attack(targeted_enemy)
                    check_if_dead(allies, enemies, battlers)
                # 施放技能
                elif "s" in cmd:
                    spell_menu(my_player, battlers, allies, enemies)
                # 使用连招
                elif "c" in cmd:
                    combo_menu(my_player, battlers, allies, enemies)
                elif "d" in cmd:
                    battler.add_combo_points(1)
                    typewriter(f"{my_player.name} 准备防御, 下一回合将受到的伤害减少50%!")
                    enhance_weapon.effect(my_player, my_player)
                    print(fx.yellow("你紧握武器, 时刻准备反击!"))
                    pass
                elif "e" in cmd:
                    if try_escape(my_player):
                        check_turns_buffs_and_debuffs(my_player, True)
                        typewriter(f"{my_player.name} 成功逃离了战斗")
                        my_player.combo_points = 0
                        return
            else:
                # 盟友自动攻击随机敌人
                if battler.is_ally:
                    if len(enemies) > 0:
                        random_enemy = random.choice(enemies)
                        battler.normal_attack(random_enemy)
                        check_if_dead(allies, enemies, battlers)
                else:
                    if len(allies) > 0:
                        # 目前敌人只会进行普通攻击，未来可扩展为完整的AI逻辑
                        random_ally = random.choice(allies)
                        battler.normal_attack(random_ally)
                        check_if_dead(allies, enemies, battlers)
        # 回合结束，检查增益和减益的持续时间
        for battler in battlers:
            check_turns_buffs_and_debuffs(battler, False)
        text.display_status_effects(battlers)

    if my_player.alive:
        # 移除所有增益和减益效果
        check_turns_buffs_and_debuffs(my_player, True)
        # 给予玩家经验值和金钱奖励
        my_player.add_exp(enemy_exp)
        my_player.add_money(enemy_money)
        # 重置连招点数
        my_player.combo_points = 0
        recover_hp_and_mp(my_player, 0.25)

def define_battlers(allies, enemies):
    battlers = enemies.copy()
    for ally in allies:
        battlers.append(ally)
    battlers.sort(key=lambda b: b.stats["agi"], reverse=True)
    return battlers

def select_target(targets):
    text.select_objective(targets)
    index = get_valid_input("> ", range(1, len(targets)+1), int)
    return targets[index - 1]

def spell_menu(my_player, battlers, allies, enemies):
    text.spell_menu(my_player)
    option = int(input("> "))
    while option not in range(len(my_player.spells)+1):
        print("请输入有效的数字")
        option = int(input("> "))
    if option != 0:
        spell_chosen = my_player.spells[option-1]
        if spell_chosen.is_targeted:
            target = select_target(battlers)
            spell_chosen.effect(my_player, target)
            check_if_dead(allies, enemies, battlers)
        else:
            if spell_chosen.default_target == "self":
                spell_chosen.effect(my_player, my_player)
            elif spell_chosen.default_target == "all_enemies":
                spell_chosen.effect(my_player, enemies)
                check_if_dead(allies, enemies, battlers)
            elif spell_chosen.default_target == "allies":
                spell_chosen.effect(my_player, allies)

def combo_menu(my_player, battlers, allies, enemies):
    text.combo_menu(my_player)
    option = int(input("> "))
    while option not in range(len(my_player.combos)+1):
        print("请输入有效的数字")
        option = int(input("> "))
    if option != 0:
        combo_chosen = my_player.combos[option-1]
        if combo_chosen.is_targeted:
            target = select_target(battlers)
            combo_chosen.effect(my_player, target)
            check_if_dead(allies, enemies, battlers)
        else:
            if combo_chosen.default_target == "self":
                combo_chosen.effect(my_player, my_player)
            elif combo_chosen.default_target == "all_enemies":
                combo_chosen.effect(my_player, enemies)
                check_if_dead(allies, enemies, battlers)

def check_miss(attacker, defender):
    miss_chance = math.floor(math.sqrt(max(0, 5 * defender.stats["agi"] - attacker.stats["agi"] * 2)))
    if miss_chance > random.randint(0, 100):
        return True
    return False

def try_escape(my_player):
    from skills import weakened_defense
    escape_chance = min(90, 35 + (my_player.stats["agi"] * 0.7 + my_player.stats["luk"] * 0.3))
    if random.randint(1, 100) <= escape_chance:
        print(fx.green("逃跑成功!"))
        return True
    else:
        print(fx.bold_red("逃跑失败!"))
        if random.random() < 0.35:
            typewriter(fx.red("你因慌乱防御力下降!"))
            weakened_defense.effect(my_player, my_player)
        return False

def check_turns_buffs_and_debuffs(target, deactivate):
    for bd in target.buffs_and_debuffs:
        bd.deactivate() if deactivate else bd.check_turns()

def check_if_dead(allies, enemies, battlers):
    dead_bodies = []
    for ally in allies:
        if ally.alive == False:
            dead_bodies.append(ally)
    for target in enemies:
        if target.alive == False:
            dead_bodies.append(target)
    for dead in dead_bodies:
        if dead in battlers:
            battlers.remove(dead)
        if dead in enemies:
            enemies.remove(dead)
        elif dead in allies:
            allies.remove(dead)

def fully_heal(target):
    target.stats["hp"] = target.stats["max_hp"]
    typewriter(f"{target.name} 的生命完全恢复了")

def fully_recover_mp(target):
    target.stats["mp"] = target.stats["max_mp"]
    typewriter(f"{target.name} 的魔法完全恢复了")

def recover_hp_and_mp(target, percent):
    target.stats["hp"] = min(target.stats["max_hp"], target.stats["hp"] + int(target.stats["max_hp"] * percent))
    target.stats["mp"] = min(target.stats["max_mp"], target.stats["mp"] + int(target.stats["max_mp"] * percent))
    typewriter(f"\n恢复了 {percent*100}% 生命值和魔法")

def get_valid_input(prompt, valid_range, cast_func=str):
    while True:
        try:
            val = cast_func(input(prompt))
            if val in valid_range:
                return val
        except:
            pass
        print("请输入有效选项")

def create_enemy_group(level, possible_enemies, enemy_quantity_for_level):
    from enemies import enemy_data

    enemies_to_appear = []
    for enemy in possible_enemies:
        low_level, high_level = possible_enemies[enemy]
        if low_level <= level <= high_level:
            enemies_to_appear.append(enemy)

    max_enemies = 1
    for max_level in enemy_quantity_for_level:
        if level < max_level:
            max_enemies = enemy_quantity_for_level[max_level]
            break

    enemy_group = []
    # 选择 x 个敌人，x 是 1 到 max_enemies 之间的随机数
    for _ in range(random.randint(1, max_enemies)):
        enemy_id = random.choice(enemies_to_appear)
        enemy_instance = deepcopy(enemy_data[enemy_id])
        enemy_group.append(enemy_instance)
    return enemy_group
