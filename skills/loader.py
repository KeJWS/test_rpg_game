import json
from typing import Dict
import core.allies as allies
from skills.skills_types import *

SPELL_CLASS_MAP: Dict[str, type] = {
    "DamageSpell": DamageSpell,
    "RecoverySpell": RecoverySpell,
    "BuffDebuffSpell": BuffDebuffSpell,
    "SummonSpell": SummonSpell,
    "AdvancedDamageSpell": AdvancedDamageSpell,
    "SlashCombo": SlashCombo,
    "ArmorBreakingCombo": ArmorBreakingCombo,
    "VampirismCombo": VampirismCombo,
    "RecoveryCombo": RecoveryCombo,
    "DamageCombo": DamageCombo,
    "MultiTargetCombo": MultiTargetCombo,
    "StunCombo": StunCombo,
}

SUMMON_CLASS_MAP = {
    "Summoned_skeleton": allies.Summoned_skeleton,
    "Summoned_fire_spirit": allies.Summoned_fire_spirit,
}

def load_skills_from_json(path="data/json_data/skills.json"):
    """
    从JSON文件加载技能定义。

    读取指定的JSON文件，解析其中的技能定义，
    并创建相应的技能实例，返回以技能名为键的字典。

    参数:
        path (str): 技能定义JSON文件的路径，默认为"data/json_data/skills.json"

    返回:
        dict: 以技能名为键，技能实例为值的字典

    异常:
        ValueError: 如果遇到未知的技能类型
        其他异常: 可能在文件读取或JSON解析中出现
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    defaults = {
        "is_targeted": True,
        "default_target": None,
    }
    skill_instances = {}
    for entry in data:
        entry = {**defaults, **entry}
        skill_type = entry.pop("type")
        if skill_type == "SummonSpell":
            entry["summoning"] = SUMMON_CLASS_MAP[entry["summoning"]]

        cls = SPELL_CLASS_MAP.get(skill_type)
        if not cls:
            raise ValueError(f"未知技能类型: {skill_type}")
        skill = cls(**entry)
        skill_instances[skill.name] = skill

    return skill_instances