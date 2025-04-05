import random

class Skill():
    def __init__(self, name, description, power, mp_cost) -> None:
        self.name = name
        self.description = description
        self.power = power
        self.mp_cost = mp_cost

class Simple_offensive_spell(Skill):
    def __init__(self, name, description, power, mp_cost) -> None:
        super().__init__(name, description, power, mp_cost)

    def effect(self, caster, target):
        if caster.stats["mp"] < self.mp_cost:
            print("没有足够的 MP")
            return 0
        else:
            base_dmg = self.power + (caster.stats["mat"]*2 - target.stats["mdf"] + caster.stats["luk"])
            dmg = round(base_dmg * random.uniform(1.0, 1.2))
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.mp_cost
            return dmg

fire_ball = Simple_offensive_spell("火球术", "", 75, 30)
