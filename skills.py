from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from combat import Battler

import random
from typing import List, Union, Callable, Optional, Dict, Any

import extensions.allies as allies


# *技能基类
class Skill:
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target

    def check_already_has_buff(self, target: Battler) -> bool:
        """检查目标是否已拥有相同的增益/减益效果"""
        for bd in target.buffs_and_debuffs:
            if bd.name == self.name:
                print(f"{target.name} 的 {self.name} 持续时间已重新开始")
                bd.restart()
                return True
        return False


# *法术类
class Spell(Skill):
    def __init__(self, name: str, description: str, power: int, cost: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.power = power

    def check_mp(self, caster: Battler) -> bool:
        """检查施法者是否有足够的MP"""
        if caster.stats["mp"] < self.cost:
            print("没有足够的 MP 释放技能")
            return False
        else:
            print(f"{caster.name} 释放了 {self.name}!")
            caster.stats["mp"] -= self.cost
            return True


# *连击类
class Combo(Skill):
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)

    def check_cp(self, caster: Battler) -> bool:
        """检查施法者是否有足够的连击点数"""
        if caster.combo_points < self.cost:
            print("没有足够的 CP 释放技能")
            return False
        else:
            print(f"{caster.name} 使用了 {self.name}!")
            caster.combo_points -= self.cost
            return True


# *伤害型法术
class Damage_spell(Spell):
    def __init__(self, name: str, description: str, power: int, mp_cost: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        
    def effect(self, caster: Battler, target: Union[Battler, List[Battler]]) -> None:
        """应用伤害效果"""
        if self.check_mp(caster):
            if self.is_targeted:
                # 单体伤害
                base_dmg = self.power + (caster.stats["mat"]*2.2 - target.stats["mdf"] + caster.stats["luk"])
                dmg = round(base_dmg * random.uniform(1.0, 1.2))
                target.take_dmg(dmg)
            else:
                # 群体伤害
                if self.default_target == "all_enemies":
                    for enemy in target:
                        base_dmg = self.power + (caster.stats["mat"]*1.5 - enemy.stats["mdf"] + caster.stats["luk"])
                        dmg = round(base_dmg * random.uniform(0.8, 1.2))
                        enemy.take_dmg(dmg)


# *回复型法术
class Recovery_spell(Spell):
    def __init__(self, name: str, description: str, power: int, mp_cost: int, stat: str, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.stat = stat

    def effect(self, caster: Battler, target: Battler) -> None:
        """应用回复效果"""
        amount_to_recover = 0
        if self.check_mp(caster):
            amount_to_recover = self.power + round(caster.stats["mat"]*2 + caster.stats["luk"])
            amount_to_recover = round(amount_to_recover * random.uniform(1.0, 1.2))

        if self.stat == "hp":
            target.heal(amount_to_recover)
        elif self.stat == "mp":
            target.recover_mp(amount_to_recover)


# *增益/减益型法术
class Buff_debuff_spell(Spell):
    def __init__(self, name: str, description: str, power: int, mp_cost: int, is_targeted: bool, default_target: str, 
                 stat_to_change: str, amount_to_change: float, turns: int) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.stat_to_change = stat_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns

    def effect(self, caster: Battler, target: Battler) -> None:
        """应用增益/减益效果"""
        if self.check_mp(caster) and not self.check_already_has_buff(target):
            buff = Buff_debuff(self.name, target, self.stat_to_change, self.amount_to_change, self.turns)
            buff.activate()


# *召唤型法术
class Summon_spell(Spell):
    def __init__(self, name: str, description: str, power: int, cost: int, is_targeted: bool, default_target: str, summoning: Callable) -> None:
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.summoning = summoning

    def effect(self, caster: Battler, allies: List[Battler]) -> None:
        """召唤盟友效果"""
        if self.check_mp(caster):
            summoning_inst = self.summoning()
            allies.append(summoning_inst)
            print(f"你召唤了 {summoning_inst.name}")


# *多次攻击型连击
class Slash_combo(Combo):
    def __init__(self, name: str, description: str, combo_cost: int, is_targeted: bool, default_target: str, time_to_hit: int) -> None:
        super().__init__(name, description, combo_cost, is_targeted, default_target)
        self.time_to_hit = time_to_hit

    def effect(self, caster: Battler, target: Battler) -> None:
        """多次攻击效果"""
        if self.check_cp(caster):
            print(f"{caster.name} 攻击 {target.name} {self.time_to_hit} 次!")
            for _ in range(self.time_to_hit):
                caster.normal_attack(target, gain_cp=False)


# *破甲型连击
class Armor_breaking_combo(Combo):
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str, armor_destroyed: float) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.armor_destroyed = armor_destroyed

    def effect(self, caster: Battler, target: Battler) -> None:
        """破甲效果"""
        if self.check_cp(caster):
            print(f"{caster.name} 刺穿了 {target.name} 的盔甲!")
            if not self.check_already_has_buff(target):
                armor_break = Buff_debuff("破甲", target, "def", self.armor_destroyed, 4)
                armor_break.activate()
                caster.normal_attack(target)


# *吸血型连击
class Vampirism_combo(Combo):
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str, percent_heal: float) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.percent_heal = percent_heal

    def effect(self, caster: Battler, target: Battler) -> None:
        """吸血效果"""
        if self.check_cp(caster):
            amount_to_recover = caster.normal_attack(target) * self.percent_heal
            caster.heal(round(amount_to_recover))


# *回复型连击
class Recovery_combo(Combo):
    def __init__(self, name: str, description: str, cost: int, stat: str, amount_to_change: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.stat = stat
        self.amount_to_change = amount_to_change
        
    def effect(self, caster: Battler, target: Battler) -> None:
        """回复效果"""
        if self.check_cp(caster):
            if self.stat == "hp":
                target.heal(self.amount_to_change)
            elif self.stat == "mp":
                target.recover_mp(self.amount_to_change)


# *伤害型连击
class Damage_combo(Combo):
    def __init__(self, name: str, description: str, power: int, cost: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.power = power

    def effect(self, caster: Battler, target: Battler) -> None:
        """高伤害效果"""
        if self.check_cp(caster):
            base_dmg = self.power + (caster.stats["atk"]*2.7 - target.stats["def"]*0.8 + caster.stats["luk"])
            dmg = round(base_dmg * random.uniform(0.8, 1.2))
            target.take_dmg(dmg)


# *状态效果基类
class Buff_debuff:
    def __init__(self, name: str, target: Battler, stat_to_change: str, amount_to_change: float, turns: int) -> None:
        self.name = name
        self.target = target
        self.stat_to_change = stat_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns
        self.max_turns = turns
        self.difference = 0

    def activate(self) -> None:
        """激活增益/减益效果"""
        self.target.buffs_and_debuffs.append(self)
        if self.amount_to_change < 0:
            print(f"{self.target.name} 的 {self.stat_to_change} 受到 {self.amount_to_change*100}% 的削弱，持续 {self.turns} 回合")
        else:
            print(f"{self.target.name} 的 {self.stat_to_change} 增益为 {self.amount_to_change*100}% 持续 {self.turns} 回合")

        self.difference = int(self.target.stats[self.stat_to_change] * self.amount_to_change)
        self.target.stats[self.stat_to_change] += self.difference

    def restart(self) -> None:
        """重置持续时间"""
        self.turns = self.max_turns

    def check_turns(self) -> None:
        """检查并更新持续时间"""
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self) -> None:
        """移除增益/减益效果"""
        print(f"\033[31m{self.name}\033[0m 的效果已结束")
        self.target.buffs_and_debuffs.remove(self)
        self.target.stats[self.stat_to_change] -= self.difference


##### 法术与连击技能实例 #####

spell_fire_ball = Damage_spell("火球术", "向单个敌人发射一颗火球", 75, 30, True, None)
spell_divine_blessing = Recovery_spell("神圣祝福", "治疗单个目标", 60, 50, "hp", True, None)
spell_enhance_weapon = Buff_debuff_spell("强化武器", "提升攻击力", 0, 32, False, "self", "atk", 0.5, 3)
spell_inferno = Damage_spell("地狱火", "对所有敌人造成伤害", 50, 55, False, "all_enemies")
spell_skeleton_summoning = Summon_spell("召唤骷髅", "召唤一个骷髅战士", 0, 42, False, "allies", allies.Summoned_skeleton)
spell_fire_spirit_summoning = Summon_spell("召唤火精灵", "召唤一个火精灵", 0, 78, False, "allies", allies.Summoned_fire_spirit)

combo_slash1 = Slash_combo("斩击连击 I", "连续攻击敌人2次", 3, True, None, 2)
combo_slash2 = Slash_combo("斩击连击 II", "连续攻击敌人3次", 3, True, None, 3)
combo_armor_breaker1 = Armor_breaking_combo("破甲 I", "破坏敌人护甲", 2, True, None, -0.3)
combo_armor_breaker2 = Armor_breaking_combo("破甲 II", "破坏敌人护甲", 3, True, None, -0.5)
combo_vampire_stab1 = Vampirism_combo("吸血之刺 I", "吸取敌人生命", 2, True, None, 0.35)
combo_vampire_stab2 = Vampirism_combo("吸血之刺 II", "吸取敌人大量生命", 2, True, None, 0.5)
combo_meditation1 = Recovery_combo("冥想 I", "恢复少量魔法", 1, "mp", 30, False, "self")
combo_meditation2 = Recovery_combo("冥想 II", "恢复大量魔法", 2, "mp", 70, False, "self")

enhance_weapon = Buff_debuff_spell("蓄力", "临时提升攻击力", 0, 0, False, "self", "atk", 0.25, 2)
weakened_defense = Buff_debuff_spell("破防", "降低防御力", 0, 0, False, "self", "def", -0.5, 2)

combo_quickSshooting1 = Slash_combo("快速连射 I", "快速射击敌人两次", 2, True, None, 2)
combo_quickSshooting2 = Slash_combo("快速连射 II", "快速射击敌人三次", 2, True, None, 3)

combo_power_slash1 = Damage_combo("力量斩 I", "蓄力一击，造成较高伤害", 130, 3, True, None)
