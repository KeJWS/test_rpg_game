import random
import allies

class Skill():
    '''
    Skill 是法术（Spells）和连招（Combos）的父类。

    Attributes:
    name : str
        技能名称。
    description : str
        技能描述。
    cost : int
        技能消耗的 MP 或 CP。
    isTargeted : bool
        如果需要选择目标则为 True，否则为 False。
    defaultTarget : str
        如果技能没有目标时的默认目标。
    '''
    def __init__(self, name, description, cost, is_targeted, default_target) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target

    def check_already_has_buff(self, target):
        '''
        检查目标单位是否已经有来自此技能的增益效果。
        技能名称必须与增益效果的名称相同。

        Parameters:
        target : Battler
            要检查的目标单位。

        Returns:
        True/False : bool
            如果目标单位已经拥有该增益效果，返回 True；否则返回 False。
        '''
        for bd in target.buffs_and_debuffs:
            if bd.name == self.name:
                print(f"{target.name} 的 {self.name} 持续时间已重新开始")
                bd.restart()
                return True
        return False

class Spell(Skill):
    '''
    法术消耗 MP（魔法值），MP 可以通过升级、使用道具、事件等恢复。它们也会随着提升 WIS（智慧）能力或装备某些物品而增加。
    法术使用 MATK（魔法攻击力）和自身的力量来计算伤害。继承自 Skill 类。

    Attributes:
    power : int
        法术的伤害值。
    '''
    def __init__(self, name, description, power, cost, is_target, default_target) -> None:
        super().__init__(name, description, cost, is_target, default_target)
        self.power = power

    def check_mp(self, caster):
        '''
        检查施法者是否有足够的 MP 来施放此法术。

        Parameters:
        caster : Battler
            施放法术的单位。

        返回：
        True/False : bool
            如果法术成功施放，返回 True；否则返回 False。
        '''
        if caster.stats["mp"] < self.cost:
            print("没有足够的 MP 释放技能")
            return False
        else:
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.cost
            return True

class Combo(Skill):
    '''
    连招消耗 CP（连招点），每次战斗开始时，CP 默认为 0，并且随着战斗单位进行普通攻击而增加。
    使用某些技能也可以增加 CP。连招通常具有特殊效果，并且结合了普通攻击。继承自 Skill 类。
    '''
    def __init__(self, name, description, cost, is_targeted, default_target) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)

    def check_cp(self, caster):
        '''
        检查施放者是否有足够的 CP 来执行连招。

        Parameters:
        caster : Battler
            执行连招的单位。

        返回：
        True/False : bool
            如果连招成功执行，返回 True；否则返回 False。
        '''
        if caster.combo_points < self.cost:
            print("没有足够的 CP 释放技能")
            return False
        else:
            print(f"{caster.name} 使用了 {self.name}!")
            caster.combo_points -= self.cost
            return True

##### 法术类 #####

class Damage_spell(Spell):
    '''
    标准的伤害法术类，继承自 Spell。
    '''
    def __init__(self, name, description, power, mp_cost, is_targeted, default_target) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)

    # TODO: 修改目标，使其始终为列表
    def effect(self, caster, target):
        '''
        根据法术的威力对目标造成伤害。

        Parameters:
        caster : Battler
            施法者。
        target : Battler/List
            法术的目标。
        '''
        if self.check_mp(caster):
            if self.is_targeted:
                base_dmg = self.power + (caster.stats["mat"]*2 - target.stats["mdf"] + caster.stats["luk"])
                dmg = round(base_dmg * random.uniform(1.0, 1.2))
                target.take_dmg(dmg)
            else:
                if self.default_target == "all_enemies":
                    for enemy in target:
                        base_dmg = self.power + (caster.stats["mat"]*1.5 - enemy.stats["mdf"] + caster.stats["luk"])
                        dmg = round(base_dmg * random.uniform(0.8, 1.2))
                        enemy.take_dmg(dmg)

class Recovery_spell(Spell):
    '''
    标准的恢复法术类，继承自 Spell。

    Attributes:
    stat : str
        要恢复的属性（mp/hp）
    '''
    def __init__(self, name, description, power, mp_cost, stat, is_targeted, default_target) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.stat =stat

    def effect(self, caster, target):
        '''
        恢复目标的某项属性。

        Parameters:
        caster : Battler
            施法者。
        target : Battler/List
            法术的目标。
        '''
        amount_to_recover = 0
        if self.check_mp(caster):
            amount_to_recover = self.power + round(caster.stats["mat"]*2 + caster.stats["luk"])
            amount_to_recover = round(amount_to_recover * random.uniform(1.0, 1.2))
        if self.stat == "hp":
            target.heal(amount_to_recover)
        elif self.stat == "mp":
            target.recover_mp(amount_to_recover)

class Buff_debuff_spell(Spell):
    '''
    标准的增益/减益法术，继承自 Spell。

    Attributes:
    statToChange : str
        要增益或减益的属性。
    amountToChange : float
        属性改变的百分比（范围 0 到 1）。
    turns : int
        增益或减益效果持续的回合数。
    '''
    def __init__(self, name, description, power, mp_cost, is_targeted, default_target, start_to_change, amount_to_change, turns) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns

    def effect(self, caster, target):
        '''
        对目标施加增益或减益效果。
        
        Parameters:
        caster : Battler
            施法者。
        target : Battler/List
            法术的目标。
        '''
        if self.check_mp(caster) and not self.check_already_has_buff(target):
            buff = Buff_debuff(self.name, target, self.start_to_change, self.amount_to_change, self.turns)
            buff.activate()

class Summon_spell(Spell):
    '''
    标准召唤法术，召唤特定的盟友。

    Attributes:
    summoning : Battler
        召唤出的战斗者。
    '''
    def __init__(self, name, description, power, cost, is_targeted, default_target, summoning) -> None:
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.summoning = summoning

    def effect(self, caster, allies):
        '''
        召唤战斗者加入战斗。

        Parameters:
        caster : Battler
            施放法术的角色。
        target : Battler/List
            施法的目标。
        '''
        if self.check_mp(caster):
            summoning_inst = self.summoning()
            allies.append(summoning_inst)
            print(f"你召唤了 {summoning_inst.name}")

##### 连击技能 #####

class Slash_combo(Combo):
    '''
    标准斩击连击（执行 X 次普通攻击）。继承自 Combo。

    Attributes:
    timesToHit : int
        普通攻击的次数。
    '''
    def __init__(self, name, description, combo_cost, is_targeted, default_target, time_to_hit) -> None:
        super().__init__(name, description, combo_cost, is_targeted, default_target)
        self.time_to_hit = time_to_hit

    def effect(self, caster, target):
        '''
        施术者对目标发动 X 次普通攻击。

        Parameters:
        caster : Battler
            施放连击的角色。
        target : Battler/List
            目标角色。
        '''
        if self.check_cp(caster):
            print(f"{caster.name} 攻击 {target.name} {self.time_to_hit} 次!")
            for _ in range(self.time_to_hit):
                caster.normal_attack(target)

class Armor_breaking_combo(Combo):
    '''
    标准护甲削弱连击。继承自 Combo。

    Attributes:
    armorDestroyed : float
        护甲削弱百分比（范围 -1 到 1，作为削弱效果应在 -1 < armorDestroyed < 0）。
    '''
    def __init__(self, name, description, cost, is_targeted, default_target, armor_destryed) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.armor_destroyed = armor_destryed

    def effect(self, caster, target):
        '''
        施术者发动普通攻击并削弱目标的护甲。

        Parameters:
        caster : Battler
            施放连击的角色。
        target : Battler/List
            目标角色。
        '''
        if self.check_cp(caster):
            print(f"{caster.name} 刺穿了 {target.name} 的盔甲!")
            if not self.check_already_has_buff(target):
                armor_break = Buff_debuff("破甲", target, "def", self.armor_destroyed, 4)
                armor_break.activate()
                caster.normal_attack(target)

class Vampirism_combo(Combo):
    '''
    标准生命吸取连击。继承自 Combo。

    Attributes:
    percentHeal : float
        根据造成的伤害恢复生命值的百分比（范围 0 到 1）。
    '''
    def __init__(self, name, description, cost, is_targeted, default_target, percent_heal) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.percent_heal = percent_heal

    def effect(self, caster, target):
        '''
        施术者发动普通攻击，并根据造成的伤害恢复生命值。

        Parameters:
        caster : Battler
            施放连击的角色。
        target : Battler/List
            目标角色。
        '''
        if self.check_cp(caster):
            amount_to_recover = caster.normal_attack(target) * self.percent_heal
            caster.heal(round(amount_to_recover))

class Recovery_combo(Combo):
    '''
    标准恢复类连击。继承自 Combo。

    Attributes:
    stat : str
        恢复的属性（mp/hp）。
    '''
    def __init__(self, name, description, cost, stat, amount_to_change, is_targeted, default_target) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def effect(self, caster, target):
        '''
        恢复目标的某项属性值。

        Parameters:
        caster : Battler
            施放连击的角色。
        target : Battler/List
            目标角色。
        '''
        if self.check_cp(caster):
            if self.stat == "hp":
                target.heal(self.amount_to_change)
            elif self.stat == "mp":
                target.recover_mp(self.amount_to_change)

##### 增益与减益状态 #####

class Buff_debuff():
    '''
    处理某项属性的增益和减益效果的类。

    Attributes:
    name : str
        增益/减益的名称（应与触发它的技能名称相同）。
    target : Battler
        受到增益/减益影响的战斗者。
    statToChange : str
        受到影响的属性。
    amountToChange : float
        属性变动的百分比（范围 -1 到 1）。
    turns : int
        剩余的回合数。
    maxTurns : int
        增益/减益的最大持续回合数（默认时长）。
    '''
    def __init__(self, name, target, start_to_change, amount_to_change, turns) -> None:
        self.name = name
        self.target = target
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns
        self.max_turns = turns
        self.difference = 0

    def activate(self):
        '''
        激活增益/减益效果。
        '''
        self.target.buffs_and_debuffs.append(self)
        if self.amount_to_change < 0:
            print(f"{self.target.name} 的 {self.start_to_change} 受到 {self.amount_to_change*100}% 的削弱，持续 {self.turns} 回合")
        else:
            print(f"{self.target.name} 的 {self.start_to_change} 增益为 {self.amount_to_change*100}% 持续 {self.turns} 回合")
        self.difference = int(self.target.stats[self.start_to_change] * self.amount_to_change)
        self.target.stats[self.start_to_change] += self.difference

    def restart(self):
        '''
        重置该增益/减益的持续回合数。
        '''
        self.turns = self.max_turns

    def check_turns(self):
        '''
        每回合减少 1 点持续时间，并检查是否应该移除该效果。
        '''
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self):
        '''
        移除增益/减益效果。
        '''
        print(f"\033[31m{self.name}\033[0m 的效果已结束")
        self.target.buffs_and_debuffs.remove(self)
        self.target.stats[self.start_to_change] -= self.difference

##### 法术与连击技能实例 #####

spell_fire_ball = Damage_spell("火球术", "", 75, 30, True, None)
spell_divine_blessing = Recovery_spell("神圣祝福", "", 60, 50, "hp", True, None)
spell_enhance_weapon = Buff_debuff_spell("强化武器", "", 0, 32, False, "self", "atk", 0.5, 3)
spell_inferno = Damage_spell("地狱火", "", 50, 55, False, "all_enemies")
spell_skeleton_summoning = Summon_spell("召唤骷髅", "", 0, 37, False, "allies", allies.Summoned_skeleton)
spell_fire_spirit_summoning = Summon_spell("召唤火精灵", "", 0, 68, False, "allies", allies.Summoned_fire_spirit)

combo_slash1 = Slash_combo("斩击连击 I", "", 3, True, None, 3)
combo_slash2 = Slash_combo("斩击连击 II", "", 3, True, None, 4)
combo_armor_breaker1 = Armor_breaking_combo("破甲 I", "", 2, True, None, -0.3)
combo_vampire_stab1 = Vampirism_combo("吸血之刺 I", "", 2, True, None, 0.35)
combo_vampire_stab2 = Vampirism_combo("吸血之刺 II", "", 2, True, None, 0.5)
combo_meditation1 = Recovery_combo("冥想 I", "", 1, "mp", 30, False, "self")
combo_meditation2 = Recovery_combo("冥想 II", "", 2, "mp", 70, False, "self")

enhance_weapon = Buff_debuff_spell("蓄力", "", 0, 0, False, "self", "atk", 0.25, 2)
weakened_defense = Buff_debuff_spell("破防", "", 0, 0, False, "self", "def", -0.5, 2)

quickSshooting = Slash_combo('快速连射 I', '', 1, True, None, 2)
quickSshooting2 = Slash_combo('快速连射 II', '', 2, True, None, 3)