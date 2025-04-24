import ast
import csv
from functools import lru_cache

import inventory, skills
from tools.load_data_from_csv import load_jewel_from_csv
from tools.dev_tools import debug_print

# ASCII 图库加载
@lru_cache(maxsize=1)
def load_ascii_art_library(filepath):
    ascii_art_dict = {}
    current_key = None
    current_lines = []

    with open(filepath, encoding='utf-8') as file:
        for line in file:
            line = line.rstrip('\n')
            if line.startswith("[") and line.endswith("]") and not line.startswith("[/"):
                current_key = line[1:-1].strip()
                current_lines = []
            elif line.startswith("[/") and line.endswith("]"):
                if current_key:
                    ascii_art_dict[current_key] = "\n".join(current_lines)
                    current_key = None
            elif current_key:
                current_lines.append(line)

    debug_print(f"加载 ASCII 艺术资源，共加载 {len(ascii_art_dict)} 项")
    return ascii_art_dict

# 装备数据加载
def load_equipment_from_csv(filepath="data/csv_data/equipments.csv"):
    equipment_dict = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            name_zh = row["name_zh"]
            description = row["description"]
            amount = int(row["amount"]) if row["amount"].strip() else 1
            individual_value = int(row["individual_value"])
            object_type = row["object_type"]
            stat_change_list = ast.literal_eval(row["stat_change_list"])
            combo_object = getattr(skills, row["combo"], None)
            spell_object = getattr(skills, row["spell"], None)

            image_path = row["image_path"]
            level = int(row["level"]) if row["level"].strip() else 1
            tags = row.get("tags", "").split(",") if row.get("tags") else []

            eq = inventory.Equipment(name_zh, description, amount, individual_value, object_type, stat_change_list, combo_object, spell_object, level, tags, image_path)
            equipment_dict[name] = eq

        debug_print(f"从 CSV 加载装备数据，共加载 {len(equipment_dict)} 项装备")
        return equipment_dict

equipment_data = load_equipment_from_csv()

def filter_equipment_by(level=None, object_type=None, tags=None, match_all_tags=False):
    result = equipment_data.values()
    if level is not None:
        result = [eq for eq in result if eq.level == level]
    if object_type:
        result = [eq for eq in result if eq.object_type == object_type]
    if tags:
        if match_all_tags:
            result = [eq for eq in result if all(tag in eq.tags for tag in tags)]
        else:
            result = [eq for eq in result if any(tag in eq.tags for tag in tags)]

    debug_print(f"筛选装备: 等级={level}, 类型={object_type}, 标签={tags}, 匹配所有标签={match_all_tags} -> {len(result)} 个结果")
    return list(result)

jack_weapon_shop_set = filter_equipment_by(level=2, object_type="weapon", tags=["weapon"])

anna_armor_shop_set = filter_equipment_by(level=2, tags=["armor", "shield", "head", "hand", "foot", "accessory"])

rik_armor_shop_item_set = filter_equipment_by(level=3, object_type="weapon", tags=["weapon"])
rik_armor_shop_item_set.extend(jack_weapon_shop_set)
rik_armor_shop_item_set.extend(filter_equipment_by(level=2, object_type="armor", tags=["armor"]))
rik_armor_shop_item_set.extend(filter_equipment_by(level=3, object_type="armor", tags=["armor"]))

lok_armor_shop_item_set = filter_equipment_by(level=3, tags=["bronze"])

jack_weapon_shop_set.append(equipment_data["war_hammer"])
rik_armor_shop_item_set.append(equipment_data["bronze_shield"])
lok_armor_shop_item_set.append(equipment_data["bronze_armor"])
lok_armor_shop_item_set.append(equipment_data["copper_ring"])

# *-> 初始装备
basic_equipments = {
    "rusty_sword": equipment_data["rusty_sword"],
    "broken_dagger": equipment_data["broken_dagger"],
    "old_staff": equipment_data["old_staff"],
    "wood_bow": equipment_data["wood_bow"],
    "novice_armor": equipment_data["novice_armor"],
    "old_robes": equipment_data["old_robes"],
}

jack_weapon_shop_set.append(basic_equipments["wood_bow"])

# 消耗品
hp_potion = inventory.Potion("生命药水 I", "恢复少量生命值的药水", 1, 25, "consumable", "hp", 70)
mp_potion = inventory.Potion("法力药水 I", "恢复少量法力值的药水", 1, 25, "consumable", "mp", 35)
hp_potion2 = inventory.Potion("生命药水 II", "恢复生命值的药水", 1, 55, "consumable", "hp", 170)
mp_potion2 = inventory.Potion("法力药水 II", "恢复法力值的药水", 1, 60, "consumable", "mp", 80)
hp_potion3 = inventory.Potion("生命药水 III", "恢复中量生命值的药水", 1, 70, "consumable", "hp", 270)
mp_potion3 = inventory.Potion("法力药水 III", "恢复中量法力值的药水", 1, 90, "consumable", "mp", 130)

jewel_data = load_jewel_from_csv()

# 魔法书
grimoire_data = [
    ("魔法书：火球术", "记载了基础的火焰魔法，释放一颗灼热火球攻击敌人。", 1, 80, skills.spell_fire_ball),
    ("魔法书：神圣祝福", "古老教会的祝文，可恢复目标生命，带来圣光的治愈。", 1, 120, skills.spell_divine_blessing),
    ("魔法书：增强武器", "魔法附魔术式，可短时间内强化武器的攻击力。", 1, 120, skills.spell_enhance_weapon),
    ("魔法书: 地狱火", "中级火焰咒文，召唤烈焰吞噬所有敌人。", 1, 210, skills.spell_inferno),
    ("唤灵书: 骷髅召唤", "记载亡灵召唤术，可呼唤骷髅战士为你作战。", 1, 195, skills.spell_skeleton_summoning),
    ("唤灵书: 火精灵", "源自炎之古国的召唤术，召唤火焰元素协助作战。", 1, 325, skills.spell_fire_spirit_summoning),
]

grimoires = [
    inventory.Grimoire(n, d, a, v, "consumable", spell)
    for (n, d, a, v, spell) in grimoire_data
]

# 商店物品套装
itz_magic_item_set = [
    equipment_data["staff"],
    equipment_data["cloth_armor"],
    hp_potion,
    mp_potion,
    equipment_data["sage_tunic"],
    equipment_data["sage_staff"],
    equipment_data["student_robes"],
    equipment_data["mana_charm"],
    *grimoires[:6],
    equipment_data["ring_of_magic"],
    jewel_data["mat_small_gems"],
]

debug_print(f"Jack 的武器商店物品数: {len(jack_weapon_shop_set)}")
debug_print(f"Anna 的护甲商店物品数: {len(anna_armor_shop_set)}")
debug_print(f"Rik 的护甲商店物品数: {len(rik_armor_shop_item_set)}")
debug_print(f"Itz 的魔法商店物品数: {len(itz_magic_item_set)}")
debug_print(f"Lok 的武具商店物品数: {len(lok_armor_shop_item_set)}")
