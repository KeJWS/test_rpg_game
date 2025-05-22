from skills import load_skills_from_json, SPELL_CLASS_MAP
from skills import ArcaneBarrage

ALL_SKILLS = load_skills_from_json()

enhance_weapon = ALL_SKILLS["蓄力"]
weakened_defense = ALL_SKILLS["破防"]

arcane_barrage = ArcaneBarrage("奥术弹幕 I", "发射多枚奥术飞弹，对敌人造成伤害", 0, 90, True, None, (3, 5))
arcane_barrage2 = ArcaneBarrage("奥术弹幕 II", "发射多枚奥术飞弹，对敌人造成伤害", 0, 145, True, None, (4, 7))

# --- 敌人技能注册 ---
SPELL_REGISTRY = {
    "enemy_fireball": SPELL_CLASS_MAP["DamageSpell"]("火球", "发射一个火球", 55, 23, True, None),
    "enemy_ice_spike": SPELL_CLASS_MAP["DamageSpell"]("冰刺", "召唤冰刺攻击敌人", 45, 17, True, None),
    "enemy_poison_sting": SPELL_CLASS_MAP["AdvancedDamageSpell"]("毒刺", "造成伤害并可能使目标中毒", 40, 27, True, None, "poison"),
    "enemy_roar": SPELL_CLASS_MAP["BuffDebuffSpell"]("怒吼", "提升自身攻击力", 0, 15, False, "self", "atk", 0.3, 3, "atk_buff"),
    "enemy_shadow_bolt": SPELL_CLASS_MAP["DamageSpell"]("暗影箭", "发射暗影能量", 70, 32, True, None),
    "enemy_heal": SPELL_CLASS_MAP["RecoverySpell"]("治疗", "恢复生命值", 50, 45, "hp", False, "self"),
    "enemy_group_attack": SPELL_CLASS_MAP["DamageSpell"]("群体攻击", "攻击所有敌人", 45, 50, False, "all_enemies"),
    "enemy_weaken": SPELL_CLASS_MAP["BuffDebuffSpell"]("削弱", "降低目标防御", 0, 25, True, None, "def", -0.3, 3, "def_debuff"),
    "enemy_stun": SPELL_CLASS_MAP["AdvancedDamageSpell"]("眩晕击", "攻击并可能眩晕目标", 50, 37, True, None, "stun"),
    # "lizard_bite": AdvancedDamageSpell("蜥蜴撕咬", "造成中等物理伤害，有几率降低目标防御", 25, 35, True, None, ""),
}
