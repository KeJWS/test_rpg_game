import math
import random
import time
import text, skills
from test.fx import dot_loading, typewriter, battle_log

from copy import deepcopy

import test.fx as fx

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
        self.combo_points = 0

    # 受到来自特定来源的伤害
    def take_dmg(self, dmg):
        from test.fx import red, bold, yellow
        """伤害结算与死亡检测"""
        dmg = max(dmg, 0)
        self.stats["hp"] -= dmg
        battle_log(f"{self.name} 受到伤害 {yellow(dmg)}", "dmg")
        time.sleep(0.3)
        if self.stats["hp"] <= 0:
            print(bold(red(f"{self.name} 被杀死了")))
            self.alive = False

    # 所有战斗者都有普通攻击
    def normal_attack(self, defender, defender_is_defending=False):
        """普通攻击逻辑（含暴击机制、防御判定）"""
        battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        if self._is_critical():
            dmg = self._calc_critical_damage(defender)
        else:
            dmg = self._calc_normal_damage(defender)

        if defender_is_defending:
            dmg = round(dmg * 0.5)
            typewriter(fx.cyan(f"{defender.name} 正在防御，伤害减半!"))

        if not check_miss(self, defender): # 检查攻击失败
            defender.take_dmg(dmg)
        else:
            dmg = 0
        return dmg

    # 检查暴击
    def _is_critical(self):
        return random.randint(1, 100) <= min(75, self.stats["crit"])

    def _calc_critical_damage(self, defender):
        crit_base = self.stats["atk"]*4 + self.stats["luk"]*1.2
        rate = random.choices([1.5, 2.0, 2.5, 3.0], weights=[50, 30, 15, 5])[0] # 暴击倍率 : 概率
        rate += self.stats["crit"]/100
        print(fx.critical(f"暴击! x{rate}"))
        dmg = round(crit_base * random.uniform(1.0, 1.2) * rate)
        battle_log(f"{self.name} 对 {defender.name} 造成了 {dmg} 点暴击伤害", "crit")
        return dmg

    def _calc_normal_damage(self, defender):
        base = self.stats["atk"]*4 - defender.stats["def"]*2
        base += self.stats["luk"] - defender.stats["luk"]
        return round(max(base, self.stats["luk"]) * random.uniform(0.8, 1.2)) # 伤害浮动：±20%

    # 目标恢复一定量的 mp
    def recover_mp(self, amount):
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        print(f"{self.name} 恢复了 {amount}MP")

    # 目标恢复一定量的生命值
    def heal(self, amount):
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        print(f"{self.name} 治愈了 {amount}HP")

    # 添加一定数量的连击点数
    def add_combo_points(self, points):
        self.combo_points += points

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
    enemy_exp = 0
    enemy_money = 0
    original_enemies = enemies.copy()
    print("=================================================")
    for enemy in enemies:
        typewriter(f"野生的 {enemy.name} 出现了!")
        enemy_exp += enemy.xp_reward
        enemy_money += enemy.gold_reward

    escaped = False

    # 只要玩家还活着，并且还有敌人需要击败，战斗就会继续
    # 战士应该根据速度变化进行更新（增益/减益）
    while player.alive and enemies:
        # 所有战斗者都被插入到战斗者列表中，并按速度（回合顺序）排序
        battlers = define_battlers(player, enemies)
        for battler in battlers:
            # 如果战斗者是盟友，则用户可以控制其行动
            if battler.is_ally:
                text.combat_menu(player, enemies)
                escaped = handle_player_turn(player, battler, enemies, battlers)
                if escaped:
                    break
            else:
                # 目前，敌人只会对玩家进行正常攻击。
                # 这可以扩展为功能性 AI
                battler.normal_attack(player, defender_is_defending=player.is_defending)

        player.is_defending = False

        if escaped:
            break

        # 一轮已过
        # 检查增益和减益效果的回合
        for b in battlers:
            check_turns_buffs_and_debuffs(b, False)
        text.display_status_effects([player] + enemies)

    if player.alive and not escaped:
        # 停用所有现有的增益效果和减益效果
        # 为玩家添加经验
        check_turns_buffs_and_debuffs(player, True)
        player.add_money(enemy_money)
        player.add_exp(enemy_exp)
        take_a_rest(player)
        # 重新开始连击点数
        player.combo_points = 0
        text.log_battle_result("胜利", player, original_enemies)
    elif escaped:
        check_turns_buffs_and_debuffs(player, True)
        typewriter(f"{player.name} 成功逃离了战斗")
        take_a_rest(player)
        player.combo_points = 0
        text.log_battle_result("逃跑", player, original_enemies)

def handle_player_turn(player, battler, enemies, battlers):
    decision = get_valid_input("> ", ["a", "d", "c", "s", "e"])
    match decision:
        case "a":
            # 进行普通攻击
            targeted_enemy = select_target(enemies)
            battler.normal_attack(targeted_enemy)
            battler.add_combo_points(1)
            check_if_dead(targeted_enemy, enemies, battlers)
        case "s":
            # 施展咒语
            text.spell_menu(battler)
            cast_spell(player, enemies, battlers)
        case "c":
            # 使用组合技能
            text.combo_menu(battler)
            cast_combo(player, enemies, battlers)
        case "d":
            player.is_defending = True
            battler.add_combo_points(1)
            typewriter(f"{player.name} 选择防御, 本回合受到的伤害将减少50%!")
        case "e":
            if try_escape(player):
                return True
            check_if_dead(player, enemies, battlers)

def cast_spell(player, enemies, battlers):
    option = get_valid_input("> ", range(len(player.spells)+1), int)
    if option == 0:
        return
    spell_chosen = player.spells[option - 1]
    if spell_chosen.is_targeted:
        target = select_target(battlers)
        spell_chosen.effect(player, target)
        check_if_dead(target, enemies, battlers)
    else:
        if spell_chosen.default_target == "self":
            spell_chosen.effect(player, player)

def cast_combo(player, enemies, battlers):
    option = get_valid_input("> ", range(len(player.combos)+1), int)
    if option == 0:
        return
    combo_chosen = player.combos[option - 1]
    if combo_chosen.is_targeted:
        target = select_target(battlers)
        combo_chosen.effect(player, target)
        check_if_dead(target, enemies, battlers)
    else:
        if combo_chosen.default_target == "self":
            combo_chosen.effect(player, player)

# 返回按速度（回合顺序）排序的战斗者列表
# 当“玩家”变为“盟友”时，应该更新此内容。
def define_battlers(player, enemies):
    return sorted(enemies.copy() + [player], key=lambda b: b.stats["agi"], reverse=True)

# 从战场上选择某个目标
def select_target(targets):
    text.select_objective(targets)
    index = get_valid_input("> ", range(1, len(targets)+1), int)
    return targets[index - 1]

# 如果攻击失败则返回 True，否则返回 False
def check_miss(attacker, defender):
    miss_chance = math.floor(math.sqrt(max(0, 5 * defender.stats["agi"] - attacker.stats["agi"] * 2)))
    if miss_chance > random.randint(0, 100):
        print(fx.red(f"{attacker.name} 的攻击被 {defender.name} 躲开了"))
        return True
    return False

def try_escape(player):
    """逃跑逻辑"""
    escape_chance = min(90, 30 + (player.stats["agi"] * 0.4 + player.stats["luk"] * 0.1))
    if random.randint(1, 100) <= escape_chance:
        print(fx.green("逃跑成功!"))
        return True
    else:
        print(fx.bold_red("逃跑失败!"))
        return False

# 检查增益和减益效果是否仍应处于活动状态
# 如果 deactivate = True，它们将立即停用
def check_turns_buffs_and_debuffs(target, deactivate):
    for bd in target.buffs_and_debuffs:
        bd.deactivate() if deactivate else bd.check_turns()

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

def get_valid_input(prompt, valid_range, cast_func=str):
    while True:
        try:
            val = cast_func(input(prompt))
            if val in valid_range:
                return val
        except:
            pass
        print("请输入有效选项")

def create_enemy_group(level):
    from enemies import possible_enemies, enemy_data

    enemies_to_appear = []
    for enemy in possible_enemies:
        low_level, high_level = possible_enemies[enemy]
        if low_level <= level <= high_level:
            enemies_to_appear.append(enemy)

    # 战斗敌人数量的字典。
    # 如果等级 < 5 -> 最多 2 个敌人
    # 如果等级 < 10 -> 最多 3 个敌人
    # ...
    enemy_quantity_for_level = {
        2: 1,
        5: 2,
        10: 3,
        100: 4
    }
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

# TODO 未来拓展技能 AI, 比如根据 HP% 或回合数使用技能
# TODO combo 和 spell 系统进一步封装, 让技能拥有 cooldown、条件触发等机制
# TODO 战斗后恢复比例（25%）可以与“露营”机制、技能、药水等组合使用
# TODO 敌人可以有“稀有出现率”字段, 例如 5% 出现某种稀有怪物
# TODO 战斗前可以加入开场事件描述, 例如“黑暗森林传来诡异的咆哮...”
