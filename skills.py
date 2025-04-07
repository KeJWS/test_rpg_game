import random

"""
技能是法术(mat)和连击(atk)的父类
"""
class Skill():
    def __init__(self, name, description, power, mp_cost) -> None:
        self.name = name
        self.description = description
        self.power = power
        self.mp_cost = mp_cost

    def check_mp(self, caster):
        if caster.stats["mp"] < self.mp_cost:
            print("没有足够的 MP 释放技能")
            return False
        else:
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.mp_cost
            return True

##### 咒语 #####

class Simple_offensive_spell(Skill):
    def __init__(self, name, description, power, mp_cost) -> None:
        super().__init__(name, description, power, mp_cost)

    def effect(self, caster, target):
        if self.check_mp(caster):
            base_dmg = self.power + (caster.stats["mat"]*2 - target.stats["mdf"] + caster.stats["luk"])
            dmg = round(base_dmg * random.uniform(1.0, 1.2))
            return dmg

class Simple_heal_spell(Skill):
    def __init__(self, name, description, power, mp_cost) -> None:
        super().__init__(name, description, power, mp_cost)

    def effect(self, caster, target):
        if self.check_mp(caster):
            amount_to_heal = self.power + round(caster.stats["mat"]*2 + caster.stats["luk"])
            return amount_to_heal
        return 0

class Buff_debuff_spell(Skill):
    def __init__(self, name, description, power, mp_cost, start_to_change, amount_to_change, turns) -> None:
        super().__init__(name, description, power, mp_cost)
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns

    def effect(self, caster, target):
        if self.check_mp(caster) and not self.check_already_has_buff(target):
            buff = Buff_debuff(self.name, target, self.start_to_change, self.amount_to_change, self.turns)
            buff.activate()

    def check_already_has_buff(self, target):
        for bd in target.buffs_and_debuffs:
            if bd.name == self.name:
                print(f"{target.name} 已经有了 {self.name}")
                return True
        return False

##### 杂项 #####

class Buff_debuff():
    def __init__(self, name, target, start_to_change, amount_to_change, turns) -> None:
        self.name = name
        self.target = target
        self.start_to_change = start_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns
        self.difference = 0

    def activate(self):
        self.target.buffs_and_debuffs.append(self)
        if self.amount_to_change < 0:
            print(f"{self.target.name} 的 {self.start_to_change} 受到 {self.amount_to_change} 的削弱，持续 {self.turns} 回合")
        else:
            print(f"{self.target.name} 的 {self.start_to_change} 增益为 {self.amount_to_change} 持续 {self.turns} 回合")
        self.difference = int(self.target.stats[self.start_to_change] * self.amount_to_change)
        self.target.stats[self.start_to_change] += self.difference

    def check_turns(self):
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self):
        print(f"\033[31m{self.name}\033[0m 的效果已结束")
        self.target.buffs_and_debuffs.remove(self)
        self.target.stats[self.start_to_change] -= self.difference

##### 咒语实例 #####

fire_ball = Simple_offensive_spell("火球术", "", 75, 30)
divineBlessing = Simple_heal_spell("神圣祝福", "", 50, 50)
benettFantasticVoyage = Buff_debuff_spell("班尼特的奇妙旅程", "", 0, 25, "atk", 0.5, 3)