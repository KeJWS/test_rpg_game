from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Callable
import random
from rich.console import Console
import core.allies as allies

if TYPE_CHECKING:
    from core.battler import Battler

console = Console()


# --- 工具函数 ---
def apply_damage(target: Battler, amount: float):
    dmg = round(amount * random.uniform(1.0, 1.2))
    target.take_dmg(dmg)
    return dmg

def apply_buff(target: Battler, name: str, stat: str, change: float, turns: int, effect_type=None):
    for buff in target.buffs_and_debuffs:
        if buff.effect_type == effect_type:
            console.print(f"{target.name} 的 {buff.name} 效果被刷新", style="cyan")
            buff.restart()
            return False
    buff = BuffDebuff(name, target, stat, change, turns, effect_type)
    buff.activate()
    return True

def heal_target(target: Battler, stat: str, amount: int):
    if stat == "hp":
        target.heal(amount)
    elif stat == "mp":
        target.recover_mp(amount)


# --- 技能基类 ---
class Skill:
    def __init__(self, name: str, description: str, cost: int, is_targeted: bool, default_target: str) -> None:
        self.name = name
        self.description = description
        self.cost = cost
        self.is_targeted = is_targeted
        self.default_target = default_target


class Spell(Skill):
    def __init__(self, name: str, description: str, power: int, cost: int, is_targeted: bool, default_target: str):
        super().__init__(name, description, cost, is_targeted, default_target)
        self.power = power

    def check_mp(self, caster: Battler) -> bool:
        if caster.stats["mp"] < self.cost:
            console.print("没有足够的 MP 释放技能", style="red")
            return False
        console.print(f"{caster.name} 释放了 {self.name}!", style="blue")
        caster.stats["mp"] -= self.cost
        return True


class Combo(Skill):
    def check_cp(self, caster: Battler) -> bool:
        if caster.combo_points < self.cost:
            console.print("没有足够的 CP 释放技能", style="red")
            return False
        console.print(f"{caster.name} 使用了 {self.name}!", style="yellow")
        caster.combo_points -= self.cost
        return True


# --- 各类技能 ---
class DamageSpell(Spell):
    def effect(self, caster: Battler, target: Union[Battler, List[Battler]]):
        if not self.check_mp(caster): return
        targets = [target] if self.is_targeted else target
        for t in targets:
            base_dmg = self.power + (caster.stats["mat"] * (2.2 if self.is_targeted else 1.5) - t.stats["mdf"] + caster.stats["luk"])
            apply_damage(t, base_dmg)


class RecoverySpell(Spell):
    def __init__(self, name, description, power, cost, stat, is_targeted, default_target):
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.stat = stat

    def effect(self, caster: Battler, target: Battler):
        if not self.check_mp(caster): return
        recover = round((self.power + caster.stats["mat"] * 2 + caster.stats["luk"]) * random.uniform(1.0, 1.2))
        heal_target(target, self.stat, recover)


class BuffDebuffSpell(Spell):
    def __init__(self, name, description, power, cost, is_targeted, default_target, stat, change, turns, effect_type=None):
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.stat_to_change = stat
        self.amount_to_change = change
        self.turns = turns
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Battler):
        if self.check_mp(caster):
            apply_buff(target, self.name, self.stat_to_change, self.amount_to_change, self.turns, self.effect_type)


class SummonSpell(Spell):
    def __init__(self, name, description, power, cost, is_targeted, default_target, summoning: Callable):
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.summoning = summoning

    def effect(self, caster: Battler, allies: List[Battler]):
        if self.check_mp(caster):
            summoned = self.summoning()
            allies.append(summoned)
            console.print(f"你召唤了 {summoned.name}", style="green")


class AdvancedDamageSpell(Spell):
    def __init__(self, name, desc, power, cost, is_targeted, default_target, effect_type=None):
        super().__init__(name, desc, power, cost, is_targeted, default_target)
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Battler):
        if not self.check_mp(caster): return
        base_dmg = self.power + (caster.stats["mat"] * 1.7 - target.stats["mdf"] + caster.stats["luk"])
        dmg = apply_damage(target, base_dmg)

        if self.effect_type == "stun" and random.random() < 0.4:
            if not any(b.effect_type == "stun" for b in target.buffs_and_debuffs):
                BuffDebuff("眩晕", target, "agi", -0.7, 2, "stun").activate()
        elif self.effect_type == "poison" and random.random() < 0.7:
            if not any(b.effect_type == "poison" for b in target.buffs_and_debuffs):
                PoisonEffect("中毒", target, "hp", -int(dmg * 0.15), 4).activate()
        elif self.effect_type == "burn" and random.random() < 0.6:
            if not any(b.effect_type == "burn" for b in target.buffs_and_debuffs):
                PoisonEffect("燃烧", target, "hp", -int(dmg * 0.3), 2).activate()


class SlashCombo(Combo):
    def __init__(self, name, desc, cost, is_targeted, default_target, hits):
        super().__init__(name, desc, cost, is_targeted, default_target)
        self.hits = hits

    def effect(self, caster: Battler, target: Battler):
        if not self.check_cp(caster): return
        console.print(f"{caster.name} 攻击 {target.name} {self.hits} 次!", style="cyan")
        for _ in range(self.hits):
            caster.normal_attack(target, gain_cp=False)


class ArmorBreakingCombo(Combo):
    def __init__(self, name, desc, cost, is_targeted, default_target, reduction, effect_type="armor_break"):
        super().__init__(name, desc, cost, is_targeted, default_target)
        self.reduction = reduction
        self.effect_type = effect_type

    def effect(self, caster: Battler, target: Battler):
        if not self.check_cp(caster): return
        if apply_buff(target, self.name, "def", self.reduction, 4, self.effect_type):
            console.print(f"{caster.name} 刺穿了 {target.name} 的盔甲!", style="red")
        caster.normal_attack(target)


class VampirismCombo(Combo):
    def __init__(self, name, desc, cost, is_targeted, default_target, percent):
        super().__init__(name, desc, cost, is_targeted, default_target)
        self.percent = percent

    def effect(self, caster: Battler, target: Battler):
        if self.check_cp(caster):
            recovered = caster.normal_attack(target) * self.percent
            caster.heal(round(recovered))


class RecoveryCombo(Combo):
    def __init__(self, name, desc, cost, stat, amount, is_targeted, default_target):
        super().__init__(name, desc, cost, is_targeted, default_target)
        self.stat = stat
        self.amount = amount

    def effect(self, caster: Battler, target: Battler):
        if self.check_cp(caster):
            heal_target(target, self.stat, self.amount)


class DamageCombo(Combo):
    def __init__(self, name, desc, power, cost, is_targeted, default_target):
        super().__init__(name, desc, cost, is_targeted, default_target)
        self.power = power

    def effect(self, caster: Battler, target: Battler):
        if self.check_cp(caster):
            dmg = self.power + (caster.stats["atk"] * 2.7 - target.stats["def"] * 0.8 + caster.stats["luk"])
            apply_damage(target, dmg)


# --- 状态类 ---
class BuffDebuff:
    def __init__(self, name, target, stat, amount, turns, effect_type=None):
        self.name = name
        self.target = target
        self.stat = stat
        self.amount = amount
        self.turns = self.max_turns = turns
        self.effect_type = effect_type
        self.difference = 0

    def activate(self):
        self.difference = int(self.target.stats[self.stat] * self.amount)
        self.target.stats[self.stat] += self.difference
        self.target.buffs_and_debuffs.append(self)
        state = "增强" if self.amount > 0 else "削弱"
        console.print(f"{self.target.name} 的 {self.stat} 被 {state}了 {abs(self.amount*100):.0f}% ，持续 {self.turns} 回合", style="green")

    def restart(self):
        self.turns = self.max_turns

    def check_turns(self):
        self.turns -= 1
        if self.turns <= 0:
            self.deactivate()

    def deactivate(self):
        self.target.stats[self.stat] -= self.difference
        self.target.buffs_and_debuffs.remove(self)
        console.print(f"[red]{self.name}[/red] 的效果已结束")


class PoisonEffect(BuffDebuff):
    def __init__(self, name, target, stat, damage_per_turn, turns, effect_type="poison"):
        super().__init__(name, target, stat, 0, turns, effect_type)
        self.damage = damage_per_turn

    def activate(self):
        self.target.buffs_and_debuffs.append(self)
        console.print(f"{self.target.name} 中了 {self.name}，每回合损失 {abs(self.damage)} HP ，持续 {self.turns} 回合", style="purple")

    def check_turns(self):
        console.print(f"{self.target.name} 因 {self.name} 受到 {abs(self.damage)} 点伤害", style="red")
        self.target.stats["hp"] += self.damage
        if self.target.stats["hp"] <= 0:
            self.target.alive = False
            console.print(f"{self.target.name} 被 {self.name} 杀死了")
        super().check_turns()


enhance_weapon = BuffDebuffSpell("蓄力", "临时提升攻击力", 0, 0, False, "self", "atk", 0.25, 2, "enhance_weapon")
weakened_defense = BuffDebuffSpell("破防", "降低防御力", 0, 0, False, "self", "def", -0.5, 2, "weakened_defense")

# 玩家法术
spell_fire_ball = DamageSpell("火球术", "向单个敌人发射一颗火球", 75, 30, True, None)
spell_divine_blessing = RecoverySpell("神圣祝福", "治疗单个目标", 60, 50, "hp", True, None)
spell_enhance_weapon = BuffDebuffSpell("强化武器", "提升攻击力", 0, 32, False, "self", "atk", 0.5, 3, "atk_buff")
spell_inferno = DamageSpell("地狱火", "对所有敌人造成伤害", 50, 55, False, "all_enemies")
spell_skeleton_summoning = SummonSpell("召唤骷髅", "召唤一个骷髅战士", 0, 42, False, "allies", allies.Summoned_skeleton)
spell_fire_spirit_summoning = SummonSpell("召唤火精灵", "召唤一个火精灵", 0, 78, False, "allies", allies.Summoned_fire_spirit)

# 玩家连击
combo_slash1 = SlashCombo("斩击连击 I", "连续攻击敌人2次", 3, True, None, 2)
combo_slash2 = SlashCombo("斩击连击 II", "连续攻击敌人3次", 3, True, None, 3)
combo_armor_breaker1 = ArmorBreakingCombo("破甲 I", "破坏敌人护甲", 3, True, None, -0.35, "armor_break")
combo_armor_breaker2 = ArmorBreakingCombo("破甲 II", "破坏敌人护甲", 3, True, None, -0.5, "armor_break")
combo_vampire_stab1 = VampirismCombo("吸血之刺 I", "吸取敌人生命", 2, True, None, 0.35)
combo_vampire_stab2 = VampirismCombo("吸血之刺 II", "吸取敌人大量生命", 2, True, None, 0.5)
combo_meditation1 = RecoveryCombo("冥想 I", "恢复少量魔法", 1, "mp", 30, False, "self")
combo_meditation2 = RecoveryCombo("冥想 II", "恢复大量魔法", 2, "mp", 70, False, "self")
combo_quickSshooting1 = SlashCombo("快速连射 I", "快速射击敌人两次", 2, True, None, 2)
combo_quickSshooting2 = SlashCombo("快速连射 II", "快速射击敌人三次", 2, True, None, 3)
combo_power_slash1 = DamageCombo("力量斩 I", "蓄力一击，造成较高伤害", 130, 3, True, None)


# --- 敌人技能注册 ---
SPELL_REGISTRY = {
    "enemy_fireball": DamageSpell("火球", "发射一个火球", 55, 23, True, None),
    "enemy_ice_spike": DamageSpell("冰刺", "召唤冰刺攻击敌人", 45, 17, True, None),
    "enemy_poison_sting": AdvancedDamageSpell("毒刺", "造成伤害并可能使目标中毒", 40, 27, True, None, "poison"),
    "enemy_roar": BuffDebuffSpell("怒吼", "提升自身攻击力", 0, 15, False, "self", "atk", 0.3, 3, "atk_buff"),
    "enemy_shadow_bolt": DamageSpell("暗影箭", "发射暗影能量", 70, 32, True, None),
    "enemy_heal": RecoverySpell("治疗", "恢复生命值", 50, 45, "hp", False, "self"),
    "enemy_group_attack": DamageSpell("群体攻击", "攻击所有敌人", 45, 50, False, "all_enemies"),
    "enemy_weaken": BuffDebuffSpell("削弱", "降低目标防御", 0, 25, True, None, "def", -0.3, 3, "atk_debuff"),
    "enemy_stun": AdvancedDamageSpell("眩晕击", "攻击并可能眩晕目标", 50, 37, True, None, "stun")
}
