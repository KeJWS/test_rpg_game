from typing import TYPE_CHECKING, List, Union, Callable
import random
from rich.console import Console
from core.skill_base import Spell, Combo

if TYPE_CHECKING:
    from core.battler import Battler

from skill.states import BuffDebuff, PoisonEffect

console = Console()


# --- 工具函数 ---
def apply_damage(target: "Battler", amount: float):
    """
    对目标应用伤害。

    基于基础伤害值计算实际伤害（含20%随机波动），
    并对目标造成伤害。

    参数:
        target (Battler): 受到伤害的目标
        amount (float): 基础伤害值

    返回:
        int: 实际造成的伤害值
    """
    dmg = round(amount * random.uniform(1.0, 1.2))
    target.take_dmg(dmg)
    return dmg

def apply_buff(target: "Battler", name: str, stat: str, change: float, turns: int, effect_type=None):
    """
    应用增益或减益效果到目标。

    检查目标当前是否已有同类型的效果，如果有则刷新持续时间，
    否则创建并激活新的效果。

    参数:
        target (Battler): 效果的目标
        name (str): 效果的名称
        stat (str): 要修改的属性名称
        change (float): 属性变化的百分比（正值为增益，负值为减益）
        turns (int): 效果持续的回合数
        effect_type: 效果类型标识，用于检查重复效果

    返回:
        bool: 如果创建了新效果返回True，如果刷新了现有效果返回False
    """
    for buff in target.buffs_and_debuffs:
        if buff.effect_type == effect_type:
            console.print(f"{target.name} 的 {buff.name} 效果被刷新", style="cyan")
            buff.restart()
            return False
    buff = BuffDebuff(name, target, stat, change, turns, effect_type)
    buff.activate()
    return True

def heal_target(target: "Battler", stat: str, amount: int):
    """
    恢复目标的生命值或魔法值。

    根据指定的属性类型调用相应的恢复方法。

    参数:
        target (Battler): 要恢复的目标
        stat (str): 要恢复的属性类型，"hp"表示生命值，"mp"表示魔法值
        amount (int): 要恢复的数量

    无返回值
    """
    if stat == "hp":
        target.heal(amount)
    elif stat == "mp":
        target.recover_mp(amount)


# --- 各类技能 ---
class DamageSpell(Spell):
    """
    伤害法术类，对目标造成伤害的法术。

    继承自Spell类，实现了基本的伤害法术效果，
    可以针对单个目标或多个目标造成伤害。
    """
    def effect(self, caster: "Battler", target: Union["Battler", List["Battler"]]):
        """
        释放伤害法术，对目标造成伤害。

        根据法术的目标类型处理单目标或多目标伤害，
        基于施法者的魔法攻击力和目标的魔法防御力计算伤害。

        参数:
            caster (Battler): 施法者
            target (Union[Battler, List[Battler]]): 法术目标，可能是单个目标或目标列表


        副作用:
            - 消耗施法者的MP
            - 对目标造成伤害
        """
        if not self.check_mp(caster): return
        targets = [target] if self.is_targeted else target
        for t in targets:
            base_dmg = self.power + (caster.stats["mat"] * (2.2 if self.is_targeted else 1.5) - t.stats["mdf"] + caster.stats["luk"])
            apply_damage(t, base_dmg)


class RecoverySpell(Spell):
    """
    恢复法术类，恢复目标生命值或魔法值的法术。

    继承自Spell类，实现了恢复生命值或魔法值的功能。

    属性:
        stat (str): 要恢复的属性类型，"hp"或"mp"
    """
    def __init__(self, name, description, power, cost, stat, is_targeted, default_target):
        """
        初始化恢复法术实例。

        除了基本法术属性外，还指定了要恢复的属性类型。

        参数:
            name (str): 法术名称
            description (str): 法术描述
            power (int): 法术基础恢复力
            cost (int): 魔法值消耗
            stat (str): 要恢复的属性，"hp"或"mp"
            is_targeted (bool): 是否需要选择目标
            default_target (str): 默认目标类型
        """
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.stat = stat

    def effect(self, caster: "Battler", target: "Battler"):
        """
        释放恢复法术，恢复目标的生命值或魔法值。

        根据法术的基础恢复力和施法者的魔法攻击力计算实际恢复量，
        并应用到目标的相应属性。

        参数:
            caster (Battler): 施法者
            target (Battler): 恢复目标


        副作用:
            - 消耗施法者的MP
            - 恢复目标的HP或MP
        """
        if not self.check_mp(caster): return
        recover = round((self.power + caster.stats["mat"] * 2 + caster.stats["luk"]) * random.uniform(1.0, 1.2))
        heal_target(target, self.stat, recover)


class BuffDebuffSpell(Spell):
    """
    增益/减益法术类，改变目标属性的法术。

    继承自Spell类，实现了增强或削弱目标某项属性的功能。

    属性:
        stat_to_change (str): 要修改的属性名称
        amount_to_change (float): 属性变化的百分比
        turns (int): 效果持续的回合数
        effect_type: 效果类型标识
    """
    def __init__(self, name, description, power, cost, is_targeted, default_target, stat, change, turns, effect_type=None):
        """
        初始化增益/减益法术实例。

        除了基本法术属性外，还指定了要修改的属性、变化量、持续时间等。

        参数:
            name (str): 法术名称
            description (str): 法术描述
            power (int): 法术基础威力
            cost (int): 魔法值消耗
            is_targeted (bool): 是否需要选择目标
            default_target (str): 默认目标类型
            stat (str): 要修改的属性名称
            change (float): 属性变化的百分比
            turns (int): 效果持续的回合数
            effect_type: 效果类型标识，用于检查重复效果
        """
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.stat_to_change = stat
        self.amount_to_change = change
        self.turns = turns
        self.effect_type = effect_type

    def effect(self, caster: "Battler", target: "Battler"):
        """
        释放增益/减益法术，改变目标的属性。

        对目标应用增益或减益效果，修改指定属性的值，
        持续一定回合数。

        参数:
            caster (Battler): 施法者
            target (Battler): 效果目标


        副作用:
            - 消耗施法者的MP
            - 改变目标的指定属性
        """
        if self.check_mp(caster):
            apply_buff(target, self.name, self.stat_to_change, self.amount_to_change, self.turns, self.effect_type)


class SummonSpell(Spell):
    """
    召唤法术类，召唤盟友参与战斗的法术。

    继承自Spell类，实现了召唤战斗单位加入友方队伍的功能。

    属性:
        summoning (Callable): 创建被召唤单位的函数
    """
    def __init__(self, name, description, power, cost, is_targeted, default_target, summoning: Callable):
        """
        初始化召唤法术实例。

        除了基本法术属性外，还指定了用于创建被召唤单位的函数。

        参数:
            name (str): 法术名称
            description (str): 法术描述
            power (int): 法术基础威力
            cost (int): 魔法值消耗
            is_targeted (bool): 是否需要选择目标
            default_target (str): 默认目标类型
            summoning (Callable): 创建被召唤单位的函数
        """
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.summoning = summoning

    def effect(self, caster: "Battler", allies: List["Battler"]):
        """
        释放召唤法术，召唤盟友加入战斗。

        通过调用指定的函数创建被召唤单位，并将其添加到友方队伍中。

        参数:
            caster (Battler): 施法者
            allies (List[Battler]): 友方队伍列表


        副作用:
            - 消耗施法者的MP
            - 向友方队伍添加新的战斗单位
        """
        if self.check_mp(caster):
            summoned = self.summoning()
            allies.append(summoned)
            console.print(f"你召唤了 {summoned.name}", style="green")


class AdvancedDamageSpell(Spell):
    """
    高级伤害法术类，除了造成伤害外还可能附加状态效果。

    继承自Spell类，实现了既造成伤害又可能附加特殊效果的法术。

    属性:
        effect_type (str): 可能附加的效果类型，如眩晕、中毒、燃烧等
    """
    def __init__(self, name, description, power, cost, is_targeted, default_target, effect_type=None):
        """
        初始化高级伤害法术实例。

        除了基本法术属性外，还指定了可能附加的效果类型。

        参数:
            name (str): 法术名称
            description (str): 法术描述
            power (int): 法术基础威力
            cost (int): 魔法值消耗
            is_targeted (bool): 是否需要选择目标
            default_target (str): 默认目标类型
            effect_type (str): 可能附加的效果类型
        """
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.effect_type = effect_type

    def effect(self, caster: "Battler", target: "Battler"):
        """
        释放高级伤害法术，对目标造成伤害并可能附加状态效果。

        根据法术效果类型，除了造成基本伤害外，还有一定
        几率附加眩晕、中毒或燃烧等状态效果。

        参数:
            caster (Battler): 施法者
            target (Battler): 法术目标

        无返回值

        副作用:
            - 消耗施法者的MP
            - 对目标造成伤害
            - 可能对目标施加状态效果
        """
        if not self.check_mp(caster): return
        base_dmg = self.power + (caster.stats["mat"] * 1.7 - target.stats["mdf"] + caster.stats["luk"])
        dmg = apply_damage(target, base_dmg)

        if self.effect_type == "stun" and random.random() < 0.4:
            if not any(b.effect_type == "stun" for b in target.buffs_and_debuffs):
                BuffDebuff("眩晕", target, "agi", -0.8, 2, "stun").activate()
        elif self.effect_type == "poison" and random.random() < 0.7:
            if not any(b.effect_type == "poison" for b in target.buffs_and_debuffs):
                PoisonEffect("中毒", target, "hp", -int(dmg * 0.12), 5).activate()
        elif self.effect_type == "burn" and random.random() < 0.6:
            if not any(b.effect_type == "burn" for b in target.buffs_and_debuffs):
                PoisonEffect("燃烧", target, "hp", -int(dmg * 0.3), 3).activate()


class ArcaneBarrage(Spell):
    """
    奥术飞弹法术类，继承自Spell。

    该法术在施法者和目标之间发射多枚奥术飞弹，造成多次普通攻击伤害。

    属性:
        min_hits (int): 最小飞弹数量。
        max_hits (int): 最大飞弹数量。
    """

    def __init__(self, name, description, power, cost, is_targeted, default_target, hits):
        """
        初始化奥术飞弹法术实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            power (int): 技能威力。
            cost (int): 技能消耗的魔法值。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            hits (tuple[int, int]): 飞弹数量范围，格式为(min_hits, max_hits)。
        """
        super().__init__(name, description, power, cost, is_targeted, default_target)
        self.min_hits = hits[0]
        self.max_hits = hits[1]

    def effect(self, caster: "Battler", target: "Battler"):
        """
        施放奥术飞弹，对目标造成多次普通攻击伤害。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者魔法值不足，技能不会生效。
        """
        if not self.check_mp(caster): return
        hits = random.randint(self.min_hits, self.max_hits)
        console.print(f"{caster.name} 对 {target.name} 发射了 {hits} 枚奥术飞弹!", style="blue")
        for _ in range(hits):
            caster.normal_attack(target, gain_cp=False)


class SlashCombo(Combo):
    """
    连击技能类，继承自Combo。

    该技能对目标进行多次普通攻击。
    """

    def __init__(self, name, description, cost, is_targeted, default_target, hits):
        """
        初始化连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            hits (int): 攻击次数。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.hits = hits

    def effect(self, caster: "Battler", target: "Battler"):
        """
        对目标进行多次普通攻击。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if not self.check_cp(caster): return
        console.print(f"{caster.name} 攻击 {target.name} {self.hits} 次!", style="cyan")
        for _ in range(self.hits):
            caster.normal_attack(target, gain_cp=False)


class ArmorBreakingCombo(Combo):
    """
    破甲连击技能类，继承自Combo。

    该技能对目标施加破甲效果并进行一次普通攻击。
    """

    def __init__(self, name, description, cost, is_targeted, default_target, reduction, effect_type="armor_break"):
        """
        初始化破甲连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            reduction (float): 破甲效果的防御力减少比例。
            effect_type (str, optional): 效果类型，默认为"armor_break"。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.reduction = reduction
        self.effect_type = effect_type

    def effect(self, caster: "Battler", target: "Battler"):
        """
        对目标施加破甲效果并进行一次普通攻击。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if not self.check_cp(caster): return
        if apply_buff(target, self.name, "def", self.reduction, 4, self.effect_type):
            console.print(f"{caster.name} 刺穿了 {target.name} 的盔甲!", style="red")
        caster.normal_attack(target, gain_cp=False)


class VampirismCombo(Combo):
    """
    吸血连击技能类，继承自Combo。

    该技能对目标造成伤害并根据伤害量回复施法者生命值。
    """

    def __init__(self, name, description, cost, is_targeted, default_target, percent):
        """
        初始化吸血连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            percent (float): 吸血比例，伤害的百分比。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.percent = percent

    def effect(self, caster: "Battler", target: "Battler"):
        """
        对目标造成伤害并回复施法者生命值。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if self.check_cp(caster):
            recovered = caster.normal_attack(target, gain_cp=False) * self.percent
            caster.heal(round(recovered))


class RecoveryCombo(Combo):
    """
    回复连击技能类，继承自Combo。

    该技能对目标回复指定属性的生命值。
    """

    def __init__(self, name, description, cost, stat, amount, is_targeted, default_target):
        """
        初始化回复连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            stat (str): 回复的属性名称。
            amount (int): 回复的数值。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.stat = stat
        self.amount = amount

    def effect(self, caster: "Battler", target: "Battler"):
        """
        对目标回复指定属性的生命值。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if self.check_cp(caster):
            heal_target(target, self.stat, self.amount)


class DamageCombo(Combo):
    """
    伤害连击技能类，继承自Combo。

    该技能对目标造成基于攻击力和技能威力的伤害。
    """

    def __init__(self, name, description, power, cost, is_targeted, default_target):
        """
        初始化伤害连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            power (int): 技能威力。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.power = power

    def effect(self, caster: "Battler", target: "Battler"):
        """
        对目标造成伤害。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if self.check_cp(caster):
            dmg = self.power + (caster.stats["atk"] * 2.7 - target.stats["def"] * 0.8 + caster.stats["luk"])
            apply_damage(target, dmg)


class MultiTargetCombo(Combo):
    """
    多目标连击技能类，继承自Combo。

    该技能对所有目标造成基于攻击力和倍率的伤害。
    """

    def __init__(self, name, description, cost, is_targeted, default_target, damage_multiplier):
        """
        初始化多目标连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            damage_multiplier (float): 伤害倍率。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.damage_multiplier = damage_multiplier

    def effect(self, caster, targets):
        """
        对所有目标造成伤害。

        参数:
            caster (Battler): 施法者对象。
            targets (list[Battler]): 目标对象列表。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if self.check_cp(caster):
            console.print(f"{caster.name} 使用了 {self.name} 攻击所有敌人!")
            for target in targets:
                dmg = caster.stats["atk"] * 4 * self.damage_multiplier - target.stats["def"] * 2.5
                apply_damage(target, dmg)


class StunCombo(Combo):
    """
    眩晕连击技能类，继承自Combo。

    该技能对目标进行普通攻击，有概率使目标进入眩晕状态。
    """

    def __init__(self, name, description, cost, is_targeted, default_target, stun_chance) -> None:
        """
        初始化眩晕连击技能实例。

        参数:
            name (str): 技能名称。
            description (str): 技能描述。
            cost (int): 技能消耗的连击点数。
            is_targeted (bool): 是否需要指定目标。
            default_target (str): 默认目标类型。
            stun_chance (float): 眩晕触发概率，范围0到1。
        """
        super().__init__(name, description, cost, is_targeted, default_target)
        self.stun_chance = stun_chance

    def effect(self, caster, target):
        """
        对目标进行普通攻击，并有概率使其进入眩晕状态。

        参数:
            caster (Battler): 施法者对象。
            target (Battler): 目标对象。

        副作用:
            Exception: 如果施法者连击点数不足，技能不会生效。
        """
        if self.check_cp(caster):
            caster.normal_attack(target, gain_cp=False)
            if random.random() < self.stun_chance:
                print(f"{caster.name} 眩晕了 {target.name}!")
                if not any(b.effect_type == "stun" for b in target.buffs_and_debuffs):
                    BuffDebuff("眩晕", target, "agi", -0.8, 2, "stun").activate()