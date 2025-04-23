from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.battler import Battler

import random
from typing import List, Union, Callable
from rich.console import Console

import core.allies as allies
console = Console()


# *技能基类
class Skill:
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target

    def check_already_has_buff(self, target: Battler, effect_type: str) -> bool:
        """检查目标是否已拥有相同的增益/减益效果"""
        for bd in target.buffs_and_debuffs:
            if getattr(bd, "effect_type", None) == effect_type:
                print(f"{target.name} 的 {bd.name} 效果被刷新")
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
            console.print("没有足够的 MP 释放技能", style="red")
            return False
        else:
            console.print(f"{caster.name} 释放了 {self.name}!", style="blue")
            caster.stats["mp"] -= self.cost
            return True


# *连击类
class Combo(Skill):
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        super().__init__(name, description, cost, is_targeted, default_target)

    def check_cp(self, caster: Battler) -> bool:
        """检查施法者是否有足够的连击点数"""
        if caster.combo_points < self.cost:
            console.print("没有足够的 CP 释放技能", style="red")
            return False
        else:
            console.print(f"{caster.name} 使用了 {self.name}!", style="yellow")
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
                 stat_to_change: str, amount_to_change: float, turns: int, effect_type: str = None) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.stat_to_change = stat_to_change
        self.amount_to_change = amount_to_change
        self.turns = turns
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Battler) -> None:
        """应用增益/减益效果"""
        if self.check_mp(caster) and not self.check_already_has_buff(target, self.effect_type):
            buff = Buff_debuff(self.name, target, self.stat_to_change, self.amount_to_change, self.turns, effect_type=self.effect_type)
            buff.activate()


# *召唤型法术
class Summon_spell(Spell):
    def __init__(self, name: str, description: str, power: int, mp_cost: int, is_targeted: bool, default_target: str, summoning: Callable) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.summoning = summoning

    def effect(self, caster: Battler, allies: List[Battler]) -> None:
        """召唤盟友效果"""
        if self.check_mp(caster):
            summoning_inst = self.summoning()
            allies.append(summoning_inst)
            print(f"你召唤了 {summoning_inst.name}")


class Advanced_damage_spell(Spell):
    def __init__(self, name: str, description: str, power: int, mp_cost: int, is_targeted: bool, default_target: str, effect_type=None) -> None:
        super().__init__(name, description, power, mp_cost, is_targeted, default_target)
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Union[Battler, List[Battler]]) -> None:
        if self.check_mp(caster):
            if self.is_targeted:
                base_dmg = self.power + (caster.stats["mat"]*1.7 - target.stats["mdf"] + caster.stats["luk"])
                dmg = round(base_dmg * random.uniform(1.0, 1.2))
                target.take_dmg(dmg)

                if self.effect_type == "stun":
                    if random.random() < 0.4:
                        if not self.check_already_has_buff(target, "stun"):
                            buff = Buff_debuff("眩晕", target, "agi", -0.7, 2, effect_type="stun")
                            buff.activate()
                elif self.effect_type == "poison":
                    if random.random() < 0.7:
                        if not self.check_already_has_buff(target, "poison"):
                            buff = Poison_effect("中毒", target, "hp", -int(dmg * 0.15), 4, effect_type="poison")
                            buff.activate()
                elif self.effect_type == "burn":
                    if random.random() < 0.6:
                        if not self.check_already_has_buff(target):
                            buff = Poison_effect("燃烧", target, "hp", -int(dmg * 0.3), 2)
                            buff.activate()

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
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str, armor_destroyed: float, effect_type: str = "armor_break") -> None:
        super().__init__(name, description, cost, is_targeted, default_target)
        self.armor_destroyed = armor_destroyed
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Battler) -> None:
        """破甲效果"""
        if self.check_cp(caster) and not self.check_already_has_buff(target, self.effect_type):
            if not self.check_already_has_buff(target, self.effect_type):
                print(f"{caster.name} 刺穿了 {target.name} 的盔甲!")
                armor_break = Buff_debuff("破甲", target, "def", self.armor_destroyed, 4, effect_type=self.effect_type)
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
    def __init__(self, name: str, target: Battler, stat_to_change: str, amount_to_change: float, turns: int, effect_type=None) -> None:
        self.name = name
        self.effect_type = effect_type
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


class Poison_effect(Buff_debuff):
    def __init__(self, name: str, target: Battler, stat, damage_per_turn, turns: int, effect_type="poison") -> None:
        super().__init__(name, target, stat, 0, turns, effect_type)
        self.damage_per_turn = damage_per_turn
        self.is_dot = True

    def activate(self) -> None:
        self.target.buffs_and_debuffs.append(self)
        print(f"{self.target.name} 受到了 {self.name} 效果，每回合损失 {abs(self.damage_per_turn)} 点生命值，持续 {self.turns} 回合")

    def check_turns(self) -> None:
        from test.fx import red
        print(f"{self.target.name} 因 {red(self.name)} 受到 {abs(self.damage_per_turn)} 点伤害")
        self.target.stats["hp"] += self.damage_per_turn
        if self.target.stats["hp"] <= 0:
            print(f"{self.target.name} 被 {self.name} 杀死了")
            self.target.alive = False
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self) -> None:
        print(f"\033[31m{self.name}\033[0m 的效果已结束")
        self.target.buffs_and_debuffs.remove(self)


##### 法术与连击技能实例 #####

spell_fire_ball = Damage_spell("火球术", "向单个敌人发射一颗火球", 75, 30, True, None)
spell_divine_blessing = Recovery_spell("神圣祝福", "治疗单个目标", 60, 50, "hp", True, None)
spell_enhance_weapon = Buff_debuff_spell("强化武器", "提升攻击力", 0, 32, False, "self", "atk", 0.5, 3, "atk_buff")
spell_inferno = Damage_spell("地狱火", "对所有敌人造成伤害", 50, 55, False, "all_enemies")
spell_skeleton_summoning = Summon_spell("召唤骷髅", "召唤一个骷髅战士", 0, 42, False, "allies", allies.Summoned_skeleton)
spell_fire_spirit_summoning = Summon_spell("召唤火精灵", "召唤一个火精灵", 0, 78, False, "allies", allies.Summoned_fire_spirit)

combo_slash1 = Slash_combo("斩击连击 I", "连续攻击敌人2次", 3, True, None, 2)
combo_slash2 = Slash_combo("斩击连击 II", "连续攻击敌人3次", 3, True, None, 3)
combo_armor_breaker1 = Armor_breaking_combo("破甲 I", "破坏敌人护甲", 3, True, None, -0.35, "armor_break")
combo_armor_breaker2 = Armor_breaking_combo("破甲 II", "破坏敌人护甲", 3, True, None, -0.5, "armor_break")
combo_vampire_stab1 = Vampirism_combo("吸血之刺 I", "吸取敌人生命", 2, True, None, 0.35)
combo_vampire_stab2 = Vampirism_combo("吸血之刺 II", "吸取敌人大量生命", 2, True, None, 0.5)
combo_meditation1 = Recovery_combo("冥想 I", "恢复少量魔法", 1, "mp", 30, False, "self")
combo_meditation2 = Recovery_combo("冥想 II", "恢复大量魔法", 2, "mp", 70, False, "self")

enhance_weapon = Buff_debuff_spell("蓄力", "临时提升攻击力", 0, 0, False, "self", "atk", 0.25, 2, "enhance_weapon")
weakened_defense = Buff_debuff_spell("破防", "降低防御力", 0, 0, False, "self", "def", -0.5, 2, "weakened_defense")

combo_quickSshooting1 = Slash_combo("快速连射 I", "快速射击敌人两次", 2, True, None, 2)
combo_quickSshooting2 = Slash_combo("快速连射 II", "快速射击敌人三次", 2, True, None, 3)

combo_power_slash1 = Damage_combo("力量斩 I", "蓄力一击，造成较高伤害", 130, 3, True, None)


# 敌人技能
enemy_fireball = Damage_spell("火球", "发射一个火球", 55, 23, True, None)
enemy_ice_spike = Damage_spell("冰刺", "召唤冰刺攻击敌人", 45, 17, True, None)
enemy_poison_sting = Advanced_damage_spell("毒刺", "造成伤害并可能使目标中毒", 40, 27, True, None, "poison")
enemy_roar = Buff_debuff_spell("怒吼", "提升自身攻击力", 0, 15, False, "self", "atk", 0.3, 3, "atk_buff")
enemy_shadow_bolt = Damage_spell("暗影箭", "发射暗影能量", 70, 32, True, None)
enemy_heal = Recovery_spell("治疗", "恢复生命值", 50, 45, "hp", False, "self")
enemy_group_attack = Damage_spell("群体攻击", "攻击所有敌人", 45, 50, False, "all_enemies")
enemy_weaken = Buff_debuff_spell("削弱", "降低目标防御", 0, 25, True, None, "def", -0.3, 3, "atk_debuff")
enemy_stun = Advanced_damage_spell("眩晕击", "攻击并可能眩晕目标", 50, 37, True, None, "stun")

SPELL_REGISTRY = {
    "enemy_fireball": enemy_fireball,
    "enemy_ice_spike": enemy_ice_spike,
    "enemy_poison_sting": enemy_poison_sting,
    "enemy_roar": enemy_roar,
    "enemy_shadow_bolt": enemy_shadow_bolt,
    "enemy_heal": enemy_heal,
    "enemy_group_attack": enemy_group_attack,
    "enemy_weaken": enemy_weaken,
    "enemy_stun": enemy_stun,
}
