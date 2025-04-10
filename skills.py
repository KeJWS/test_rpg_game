import random

"""
技能是法术(mat)和连击(atk)的父类
"""
class Skill():
    def __init__(self, name, description, cost, is_targeted, default_target) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target

    def check_already_has_buff(self, target):
        for bd in target.buffs_and_debuffs:
            if bd.name == self.name:
                print(f"{target.name} 的 {self.name} 持续时间已重新开始")
                bd.restart()
                return True
        return False

"""
法术会消耗魔法值(mp), 魔法值会通过升级、使用物品、
事件等方式恢复。提升智慧(WIS)资质或装备特定物品时, 魔法值也会增加。法术会根据魔法攻击力(matk)和自身力量来计算造成的伤害。
"""

class Spell(Skill):
    def __init__(self, name, description, power, cost, is_target, default_target) -> None:
        super().__init__(name, description, cost, is_target, default_target)
        self.power = power

    def check_mp(self, caster):
        if caster.stats["mp"] < self.cost:
            print("没有足够的 MP 释放技能")
            return False
        else:
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.cost
            return True

"""
连击会消耗cp(连击点数), 战斗开始时cp默认为0, 战斗者进行普通攻击时cp会增加。使用特定技能也会增加cp。连击通常具有特殊效果, 并包含普通攻击。
"""

class Combo(Skill):
    def __init__(self, name, description, cost, is_targeted, default_target) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)

    def check_cp(self, caster):
        if caster.combo_points < self.cost:
            print("没有足够的 CP 释放技能")
            return False
        else:
            print(f"{caster.name} 使用了 {self.name}!")
            caster.combo_points -= self.cost
            return True

##### 咒语 #####

class Damage_spell(Spell):
    def __init__(self, name, description, power, mp_cost, is_targeted, default_target) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)

    def effect(self, caster, target):
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
    def __init__(self, name, description, power, mp_cost, stat, is_targeted, default_target) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.stat =stat

    def effect(self, caster, target):
        amount_to_recover = 0
        if self.check_mp(caster):
            amount_to_recover = self.power + round(caster.stats["mat"]*2 + caster.stats["luk"])
            amount_to_recover = round(amount_to_recover * random.uniform(1.0, 1.2))
        if self.stat == "hp":
            target.heal(amount_to_recover)
        elif self.stat == "mp":
            target.recover_mp(amount_to_recover)

class Buff_debuff_spell(Spell):
    def __init__(self, name, description, power, mp_cost, is_targeted, default_target, start_to_change, amount_to_change, turns) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns

    def effect(self, caster, target):
        if self.check_mp(caster) and not self.check_already_has_buff(target):
            buff = Buff_debuff(self.name, target, self.start_to_change, self.amount_to_change, self.turns)
            buff.activate()

##### 连击 #####

class Slash_combo(Combo):
    def __init__(self, name, description, combo_cost, is_targeted, default_target, time_to_hit) -> None:
        super().__init__(name, description, combo_cost, is_targeted, default_target)
        self.time_to_hit = time_to_hit

    def effect(self, caster, target):
        if self.check_cp(caster):
            print(f"{caster.name} 攻击 {target.name} {self.time_to_hit} 次!")
            for _ in range(self.time_to_hit):
                caster.normal_attack(target)

class Armor_breaking_combo(Combo):
    def __init__(self, name, description, cost, is_targeted, default_target, armor_destryed) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.armor_destroyed = armor_destryed

    def effect(self, caster, target):
        if self.check_cp(caster):
            print(f"{caster.name} 刺穿了 {target.name} 的盔甲!")
            if not self.check_already_has_buff(target):
                armor_break = Buff_debuff("破甲", target, "def", self.armor_destroyed, 4)
                armor_break.activate()
                caster.normal_attack(target)

class Vampirism_combo(Combo):
    def __init__(self, name, description, cost, is_targeted, default_target, percent_heal) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.percent_heal = percent_heal

    def effect(self, caster, target):
        if self.check_cp(caster):
            amount_to_recover = caster.normal_attack(target) * self.percent_heal
            caster.heal(round(amount_to_recover))

class Recovery_combo(Combo):
    def __init__(self, name, description, cost, stat, amount_to_change, is_targeted, default_target) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def effect(self, caster, target):
        if self.check_cp(caster):
            if self.stat == "hp":
                target.heal(self.amount_to_change)
            elif self.stat == "mp":
                target.recover_mp(self.amount_to_change)

##### 杂项 #####

class Buff_debuff():
    def __init__(self, name, target, start_to_change, amount_to_change, turns) -> None:
        self.name = name
        self.target = target
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns
        self.max_turns = turns
        self.difference = 0

    def activate(self):
        self.target.buffs_and_debuffs.append(self)
        if self.amount_to_change < 0:
            print(f"{self.target.name} 的 {self.start_to_change} 受到 {self.amount_to_change*100}% 的削弱，持续 {self.turns} 回合")
        else:
            print(f"{self.target.name} 的 {self.start_to_change} 增益为 {self.amount_to_change*100}% 持续 {self.turns} 回合")
        self.difference = int(self.target.stats[self.start_to_change] * self.amount_to_change)
        self.target.stats[self.start_to_change] += self.difference

    def restart(self):
        self.turns = self.max_turns

    def check_turns(self):
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self):
        print(f"\033[31m{self.name}\033[0m 的效果已结束")
        self.target.buffs_and_debuffs.remove(self)
        self.target.stats[self.start_to_change] -= self.difference

##### 法术和连击实例 #####

spell_fire_ball = Damage_spell("火球术", "", 75, 30, True, None)
spell_divine_blessing = Recovery_spell("神圣祝福", "", 60, 50, "hp", True, None)
spell_enhance_weapon = Buff_debuff_spell("强化武器", "", 0, 30, False, "self", "atk", 0.5, 3)
spell_inferno = Damage_spell("地狱火", "", 50, 50, False, "all_enemies")

combo_slash1 = Slash_combo("斩击连击 I", "", 3, True, None, 3)
combo_slash2 = Slash_combo("斩击连击 II", "", 3, True, None, 4)
combo_armor_breaker1 = Armor_breaking_combo("破甲 I", "", 2, True, None, -0.3)
combo_vampire_stab1 = Vampirism_combo("吸血之刺 I", "", 2, True, None, 0.5)
combo_vampire_stab2 = Vampirism_combo("吸血之刺 II", "", 2, True, None, 0.75)
combo_meditation1 = Recovery_combo("冥想 I", "", 1, "mp", 30, False, "self")
combo_meditation2 = Recovery_combo("冥想 II", "", 2, "mp", 70, False, "self")


enhance_weapon = Buff_debuff_spell("蓄力", "", 0, 0, False, "self", "atk", 0.25, 2)
weakened_defense = Buff_debuff_spell("破防", "", 0, 0, False, "self", "def", -0.5, 2)
