import random

from os import times
from typing import cast

"""
技能是法术(mat)和连击(atk)的父类
"""
class Skill():
    def __init__(self, name, description, cost, is_targeted) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted

    def check_already_has_buff(self, target):
        for bd in target.buffs_and_debuffs:
            if bd.name == self.name:
                print(f"{target.name} 的 {self.name} 持续时间已重新开始")
                bd.restart()
                return True
        return False

class Spell(Skill):
    def __init__(self, name, description, power, cost, is_target) -> None:
        super().__init__(name, description, cost, is_target)
        self.power = power

    def check_mp(self, caster):
        if caster.stats["mp"] < self.cost:
            print("没有足够的 MP 释放技能")
            return False
        else:
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.cost
            return True

class Combo(Skill):
    def __init__(self, name, description, cost, is_targeted) -> None:
        super().__init__(name, description, cost, is_targeted)

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
    def __init__(self, name, description, power, mp_cost, is_targeted) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted)

    def effect(self, caster, target):
        if self.check_mp(caster):
            base_dmg = self.power + (caster.stats["mat"]*2 - target.stats["mdf"] + caster.stats["luk"])
            dmg = round(base_dmg * random.uniform(1.0, 1.2))
        target.take_dmg(dmg)

class Healing_spell(Spell):
    def __init__(self, name, description, power, mp_cost, is_targeted) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted)

    def effect(self, caster, target):
        amount_to_heal = 0
        if self.check_mp(caster):
            amount_to_heal = self.power + round(caster.stats["mat"]*2 + caster.stats["luk"])
        target.heal(amount_to_heal)

class Buff_debuff_spell(Spell):
    def __init__(self, name, description, power, mp_cost, is_targeted, start_to_change, amount_to_change, turns) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted)
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns

    def effect(self, caster, target):
        if self.check_mp(caster) and not self.check_already_has_buff(target):
            buff = Buff_debuff(self.name, target, self.start_to_change, self.amount_to_change, self.turns)
            buff.activate()

##### 连击 #####

class Slash_combo(Combo):
    def __init__(self, name, description, combo_cost, is_targeted, time_to_hit) -> None:
        super().__init__(name, description, combo_cost, is_targeted)
        self.time_to_hit = time_to_hit

    def effect(self, caster, target):
        if self.check_cp(caster):
            print(f"{caster.name} 攻击 {target.name} {self.time_to_hit} 次!")
            for _ in range(self.time_to_hit):
                caster.normal_attack(target)

class Armor_breaking_combo(Combo):
    def __init__(self, name, description, cost, is_targeted, armor_destryed) -> None:
        super().__init__(name, description, cost, is_targeted)
        self.armor_destroyed = armor_destryed

    def effect(self, caster, target):
        if self.check_cp(caster):
            print(f"{caster.name} 刺穿了 {target.name} 的盔甲!")
            if not self.check_already_has_buff(target):
                armor_break = Buff_debuff("Armor Break", target, "def", self.armor_destroyed, 4)
                armor_break.activate()
                caster.normal_attack(target)

class Vampirism_combo(Combo):
    def __init__(self, name, description, cost, is_targeted, percent_heal) -> None:
        super().__init__(name, description, cost, is_targeted)
        self.percent_heal = percent_heal

    def effect(self, caster, target):
        if self.check_cp(caster):
            amount_to_recover = caster.normal_attack(target) * self.percent_heal
            caster.heal(round(amount_to_recover))

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

fire_ball = Damage_spell("火球术", "", 75, 30, True)
divineBlessing = Healing_spell("神圣祝福", "", 50, 50, True)
benettFantasticVoyage = Buff_debuff_spell("班尼特的奇妙旅程", "", 0, 25, False, "atk", 0.5, 3)

slash_combo1 = Slash_combo("斩击连击 I", "", 3, True, 3)
armor_breaker1 = Armor_breaking_combo("破甲 I", "", 2, True, -0.3)
vampire_stab1 = Vampirism_combo("吸血之刺", "", 2, True, 0.5)
