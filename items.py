import ast
import csv
from functools import lru_cache

import skills
import others.item as item
from others.equipment import Equipment
from tools.load_data_from_csv import load_jewel_from_csv, load_food_from_csv
from tools.dev_tools import debug_print

# 缓存加载 ASCII 艺术资源
@lru_cache(maxsize=1)
def load_ascii_art_library(filepath):
    ascii_art_dict = {}
    current_key = None
    current_lines = []

    with open(filepath, encoding='utf-8') as file:
        for line in file:
            line = line.rstrip('\n')
            if line.startswith("[") and line.endswith("]"):
                if line.startswith("[/"):  # 结束标签
                    if current_key:
                        ascii_art_dict[current_key] = "\n".join(current_lines)
                        current_key = None
                else:  # 起始标签
                    current_key = line[1:-1].strip()
                    current_lines = []
            elif current_key:
                current_lines.append(line)

    debug_print(f"加载 ASCII 艺术资源，共加载 {len(ascii_art_dict)} 项")
    return ascii_art_dict

# 加载装备数据
def load_equipment_from_csv(filepath="data/csv_data/equipments.csv", skill_dict=skills.skills):
    if skill_dict is None:
        skill_dict = {}

    equipment_dict = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        for row in csv.DictReader(csvfile):
            name = row["name"]

            combo_name = row.get("combo", "").strip()
            spell_name = row.get("spell", "").strip()
            kwargs = {
                "name": row["name_zh"],
                "description": row["description"],
                "amount": 1,
                "individual_value": int(row["individual_value"]) if row["individual_value"].strip() else 0,
                "object_type": row["object_type"],
                "stat_change_list": ast.literal_eval(row["stat_change_list"]),
                "combo": skill_dict.get(combo_name) if combo_name else None,
                "spell": skill_dict.get(spell_name) if spell_name else None,
                "level": int(row["level"]) if row["level"].strip() else 0,
                "tags": row.get("tags", "").split(",") if row.get("tags") else [],
                "image_path": row.get("image_path", "")
            }

            equipment_dict[name] = Equipment(**kwargs)

    debug_print(f"从 CSV 加载装备数据，共加载 {len(equipment_dict)} 项装备")
    return equipment_dict

equipment_data = load_equipment_from_csv()

# 装备筛选器
def filter_equipment_by(level=None, object_type=None, tags=None, match_all_tags=False):
    result = equipment_data.values()

    if level is not None:
        result = filter(lambda eq: eq.level == level, result)
    if object_type:
        result = filter(lambda eq: eq.object_type == object_type, result)
    if tags:
        if match_all_tags:
            result = filter(lambda eq: all(tag in eq.tags for tag in tags), result)
        else:
            result = filter(lambda eq: any(tag in eq.tags for tag in tags), result)

    result = list(result)
    debug_print(f"筛选装备: 等级={level}, 类型={object_type}, 标签={tags}, 匹配所有标签={match_all_tags} -> {len(result)} 个结果")
    return result

# 定义商店物品
jack_weapon_shop_set = filter_equipment_by(level=2, object_type="weapon", tags=["weapon"])
anna_armor_shop_set = filter_equipment_by(level=2, tags=["armor", "shield", "head", "hand", "foot", "accessory"])

rik_armor_shop_item_set = (
    filter_equipment_by(level=3, object_type="weapon", tags=["weapon"])
    + jack_weapon_shop_set
    + filter_equipment_by(level=2, object_type="armor", tags=["armor"])
    + filter_equipment_by(level=3, object_type="armor", tags=["armor"])
)

lok_armor_shop_item_set = filter_equipment_by(level=3, tags=["bronze"])

mysterious_businessman_shop_item_set = filter_equipment_by(level=2)

# 加入特殊指定装备
jack_weapon_shop_set.append(equipment_data["war_hammer"])
rik_armor_shop_item_set.append(equipment_data["bronze_shield"])
lok_armor_shop_item_set += [equipment_data["bronze_armor"], equipment_data["copper_ring"]]

# 初始装备
basic_equipments = {
    "rusty_sword": equipment_data["rusty_sword"],
    "broken_dagger": equipment_data["broken_dagger"],
    "old_staff": equipment_data["old_staff"],
    "wood_bow": equipment_data["wood_bow"],
    "wooden_club": equipment_data["wooden_club"],
    "training_dagger": equipment_data["training_dagger"],
    "beginner_wand": equipment_data["beginner_wand"],
    "self_bow": equipment_data["self_bow"],

    "novice_armor": equipment_data["novice_armor"],
    "old_robes": equipment_data["old_robes"],
    "padded_vest": equipment_data["padded_vest"],
}

# 药水类物品
hp_potion = item.Potion("生命药水 I", "恢复少量生命值的药水", 1, 25, "consumable", "hp", 70)
mp_potion = item.Potion("法力药水 I", "恢复少量法力值的药水", 1, 25, "consumable", "mp", 35)
hp_potion2 = item.Potion("生命药水 II", "恢复生命值的药水", 1, 55, "consumable", "hp", 170)
mp_potion2 = item.Potion("法力药水 II", "恢复法力值的药水", 1, 60, "consumable", "mp", 80)
hp_potion3 = item.Potion("生命药水 III", "恢复中量生命值的药水", 1, 70, "consumable", "hp", 270)
mp_potion3 = item.Potion("法力药水 III", "恢复中量法力值的药水", 1, 90, "consumable", "mp", 130)

# 材料类
def item_factory(name: str, amount: int = 1):
    if name == "魔法草":
        return item.Item("魔法草", "散发魔力的草药", amount, 30, "material")
    elif name == "狼皮":
        return item.Item("狼皮", "一张完整的野狼皮", amount, 45, "material")
    elif name == "凝胶":
        return item.Item("凝胶", "像果冻一样...", amount, 10, "material")
    elif name == "蛛丝":
        return item.Item("蛛丝", "击败蜘蛛后的掉落物", amount, 12, "material")
    else:
        return None

# 食物数据
food_data = load_food_from_csv()
bread = food_data["bread"]

# 宝石数据
jewel_data = load_jewel_from_csv()

# 魔法书数据构造
grimoire_data = [
    ("魔法书：火球术", "基础火焰魔法，释放灼热火球。", 1, 80, skills.skills["火球术"]),
    ("魔法书：神圣祝福", "可恢复生命，带来圣光的治愈。", 1, 120, skills.skills["神圣祝福"]),
    ("魔法书：增强武器", "短时间内强化武器攻击力。", 1, 120, skills.skills["强化武器"]),
    ("魔法书: 地狱火", "召唤烈焰吞噬所有敌人。", 1, 210, skills.skills["地狱火"]),
    ("唤灵书: 骷髅召唤", "召唤骷髅战士作战。", 1, 195, skills.skills["召唤骷髅"]),
    ("唤灵书: 火精灵", "召唤火焰元素协助作战。", 1, 325, skills.skills["召唤火精灵"]),
]
grimoires = [item.Grimoire(n, d, a, v, "consumable", s) for n, d, a, v, s in grimoire_data]

mary_food_stall_set = [
    bread, bread, bread,
    food_data["mushroom_soup"],
    food_data["meat_skewer"],
    food_data["honey_apple"],
    food_data["mary_cookie"],
]

itz_magic_item_set = [
    equipment_data["staff"],
    equipment_data["cloth_armor"],
    hp_potion, hp_potion,
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
debug_print(f"Mary 的食品商店物品数: {len(mary_food_stall_set)}")
debug_print(f"Rik 的护甲商店物品数: {len(rik_armor_shop_item_set)}")
debug_print(f"Itz 的魔法商店物品数: {len(itz_magic_item_set)}")
debug_print(f"Lok 的武具商店物品数: {len(lok_armor_shop_item_set)}")
debug_print(f"神秘商人的物品数: {len(mysterious_businessman_shop_item_set)}")
