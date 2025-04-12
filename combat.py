import math
import random
import time
import text
from test.fx import dot_loading, typewriter, battle_log

from copy import deepcopy

import test.fx as fx

class Battler():
    '''
    所有可以参与战斗的实例的父类。
    Battler 将始终是敌人、玩家的盟友或玩家本人。

    Attributes:
    name : str
        战斗者的名称。
    stats : dict
        战斗者的属性，字典格式，例如：{'atk' : 3}。
    alive : bool              
        表示战斗者是否存活的布尔值。
    buffsAndDebuffs : list     
        战斗者当前拥有的增益和减益列表。
    isAlly : bool             
        表示战斗者是否为玩家的盟友的布尔值。
    '''
    def __init__(self, name, stats) -> None:
        self.name = name
        self.stats = stats
        self.alive = True
        self.buffs_and_debuffs = []
        self.is_ally = False
        self.is_defending = False

    def take_dmg(self, dmg):
        '''
        战斗者受到来自任何来源的伤害的函数。
        从其生命值中减去伤害量，同时检查是否死亡。

        Parameters:
        dmg : int     
            造成的伤害数量
        '''
        from test.fx import red, bold, yellow
        """伤害结算与死亡检测"""
        dmg = max(dmg, 0)
        self.stats["hp"] -= dmg
        battle_log(f"{self.name} 受到伤害 {yellow(dmg)}", "dmg")
        time.sleep(0.3)
        # 防御者死亡
        if self.stats["hp"] <= 0:
            print(bold(red(f"{self.name} 被杀死了")))
            self.alive = False

    def normal_attack(self, defender, defender_is_defending=False):
        '''
        所有战斗者都有的普通攻击。

        伤害计算如下：
        attacker_atk * (100 / (100 + defender_def * 1.5))

        Parameters:
        defender : Battler
            防御的战斗者

        Returns:
        dmg : int        
            对防御者造成的伤害
        '''
        battle_log(f"{self.name} 发动攻击!", "info")
        dot_loading()

        # 检查是否攻击未命中
        if check_miss(self,defender):
            print(fx.red(f"{self.name} 的攻击被 {defender.name} 躲开了"))
            return 0
        # 检查是否为暴击
        if self._is_critical():
            dmg = self._calc_critical_damage(defender)
        else:
            dmg = self._calc_normal_damage(defender)

        if defender_is_defending:
            dmg = round(dmg * 0.5)
            typewriter(fx.cyan(f"{defender.name} 正在防御，伤害减半!"))
        defender.take_dmg(dmg)
        return dmg

    def _is_critical(self):
        '''
        检查攻击是否为暴击。如果是，则伤害翻倍。

        暴击几率来源于战斗者的属性：'critCh'

        Parameters:
        dmg : int     
            基础伤害

        Returns:
        dmg : int 
            经过检查和处理后的伤害
        '''
        return random.randint(1, 100) <= min(72, round(self.stats["crit"]*0.8+self.stats["luk"]*0.2))

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

    def recover_mp(self, amount):
        '''
        战斗者恢复一定量的 'mp'（法力值）。

        Parameters:
        amount : int      
            恢复的法力值
        '''
        self.stats["mp"] = min(self.stats["mp"] + amount, self.stats["max_mp"])
        typewriter(fx.blue(f"{self.name} 恢复了 {amount}MP"))

    def heal(self, amount):
        '''
        战斗者恢复一定量的 'hp'（生命值）。

        Parameters:
        amount : int     
            恢复的生命值
        '''
        self.stats["hp"] = min(self.stats["hp"] + amount, self.stats["max_hp"])
        typewriter(fx.green(f"{self.name} 治愈了 {amount}HP"))

class Enemy(Battler):
    '''
    所有敌人的基类。继承自 'Battler' 类。

    Attributes:
    xpReward : int    
        被击杀时给予的经验值（XP）数量
    goldReward : int 
        被击杀时给予的金币数量
    '''
    def __init__(self, name, stats, xp_reward, gold_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.original_stats = stats.copy()

    def clone(self):
        new_stats = self.original_stats.copy()
        return Enemy(self.name, new_stats, self.xp_reward, self.gold_reward)

"""
主战斗循环
"""

def combat(my_player, enemies):
    from player import Player
    '''
    处理玩家与敌人之间的主要战斗循环。

    Parameters:
    myPlayer : Player
        当前玩家对象
    enemies : list     
        需要战斗的敌人列表

    备注:
    如果战斗支持多个盟友，应将 myPlayer 替换为名为 'allies' 的列表。
    目前，只有通过召唤技能才能获得盟友，因此暂未做此修改。
    '''
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
                    pass
                elif "e" in cmd:
                    pass
            else:
                # 盟友自动攻击随机敌人
                if battler.is_ally:
                    if len(enemies) > 0:
                        random_enemy = random.choice(enemies)
                        battler.normal_attack(random_enemy)
                        check_if_dead(allies, enemies, battlers)
                else:
                    # 目前敌人只会进行普通攻击，未来可扩展为完整的AI逻辑
                    random_ally = random.choice(allies)
                    battler.normal_attack(random_ally)
                    check_if_dead(allies, enemies, battlers)
        # 回合结束，检查增益和减益的持续时间
        for battler in battlers:
            check_turns_buffs_and_debuffs(battler, False)

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
    '''
    返回战斗单位列表，并按速度排序（决定回合顺序）。

    Parameters:
    allies : List
        盟友单位列表
    enemies : List
        敌方单位列表

    Returns:
    battlers : List
        包含敌人和盟友的战斗单位列表，按速度排序
    '''
    battlers = enemies.copy()
    for ally in allies:
        battlers.append(ally)
    battlers.sort(key=lambda b: b.stats["agi"], reverse=True)
    return battlers

def select_target(targets):
    '''
    从战场中选择一个目标。

    Parameters:
    targets : list
        可选目标单位列表

    Return:
    target : Battler
        选中的目标
    '''
    text.select_objective(targets)
    index = get_valid_input("> ", range(1, len(targets)+1), int)
    return targets[index - 1]

def spell_menu(my_player, battlers, allies, enemies):
    '''
    让玩家选择一个目标施放法术。

    Parameters:
    myPlayer : Player
        施放法术的玩家。
    battlers : List
        战斗中的所有参战者列表。
    allies : List
        友方单位列表。
    enemies : List
        敌方单位列表。
    '''
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
    '''
    让玩家选择一个目标执行连招。

    Parameters:
    myPlayer : Player
        进行连招的玩家。
    battlers : List
        战斗中的所有参战者列表。
    allies : List
        友方单位列表。
    enemies : List
        敌方单位列表。
    '''
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
    '''
    检查攻击是否命中，命中率由以下公式决定：

    chance = math.floor(math.sqrt(max(0, (5 * defender.stats['speed'] - attacker.stats['speed'] * 2))))

    经过多次尝试，这个公式表现得相对合理。当然，你可以根据需要进行调整。

    Parameters:
    attacker : Battler
        发起攻击的单位。
    defender : Battler
        受到攻击的单位。

    Returns:
    True/False : Bool
        True 代表攻击未命中，False 代表攻击命中。
    '''
    miss_chance = math.floor(math.sqrt(max(0, 5 * defender.stats["agi"] - attacker.stats["agi"] * 2)))
    if miss_chance > random.randint(0, 100):
        typewriter(fx.red(f"{attacker.name} 的攻击被 {defender.name} 躲开了"))
        return True
    return False

def try_escape(my_player):
    from skills import weakened_defense
    """逃跑逻辑"""
    escape_chance = min(90, 30 + (my_player.stats["agi"] * 0.4 + my_player.stats["luk"] * 0.1))
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
    '''
    检查目标的增益和减益状态是否仍然有效（基于回合数判断）。

    Parameters:
    target : Battler
        需要检查状态的单位。
    deactivate : bool
        若为 True，则立即清除所有增益和减益状态（适用于战斗结束等情况）。
        若为 False，则正常检测状态回合数。
    '''
    for bd in target.buffs_and_debuffs:
        bd.deactivate() if deactivate else bd.check_turns()

def check_if_dead(allies, enemies, battlers):
    '''
    检查战斗单位是否阵亡，如果阵亡，则从相应列表中移除。

    Parameters:
    allies : List
        友方单位列表。
    enemies : List
        敌方单位列表。
    battlers : List
        参战单位总列表。
    '''
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
    '''
    完全恢复目标的生命值。

    Parameters:
    target : Battler
        需要恢复的单位。
    '''
    target.stats["hp"] = target.stats["max_hp"]
    typewriter(f"{target.name} 的生命完全恢复了")

def fully_recover_mp(target):
    '''
    完全恢复目标的魔法值。

    Parameters:
    target : Battler
        需要恢复的单位。
    '''
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
    '''
    根据玩家等级创建敌人小队。

    Parameters:
    lvl : int
        玩家当前等级。
    possible_enemies : Dictionary
        可能出现的敌人及其对应的等级范围，
        采用以下格式：{enemyClass : (最低等级, 最高等级)}
    enemy_quantity_for_level : Dictionary
        根据玩家等级决定敌人数量，
        格式示例：{等级上限 : 敌人数量}，
        例如 {3: 1} 表示 3 级及以下最多出现 1 名敌人。

    Returns:
    enemy_group : List
        生成的敌人单位列表。
    '''

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

# TODO 未来拓展技能 AI, 比如根据 HP% 或回合数使用技能
# TODO combo 和 spell 系统进一步封装, 让技能拥有 cooldown、条件触发等机制
# TODO 战斗后恢复比例（25%）可以与“露营”机制、技能、药水等组合使用
# TODO 敌人可以有“稀有出现率”字段, 例如 5% 出现某种稀有怪物
