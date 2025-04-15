import csv, ast
from functools import lru_cache

import inventory, skills

# ASCII 图库加载
@lru_cache(maxsize=1)
def load_ascii_art_library(filepath="data/ascii_art_equipment.txt"):
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

    return ascii_art_dict

# 装备数据加载
def load_equipment_from_csv(filepath="data/equipments.csv"):
    equipment_dict = {}
    ascii_art_dict = load_ascii_art_library()
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            name_zh = row["name_zh"]
            description = row["description"]
            amount = int(row["amount"])
            individual_value = int(row["individual_value"])
            object_type = row["object_type"]
            stat_change_list = ast.literal_eval(row["stat_change_list"])
            combo_object = getattr(skills, row["combo"], None)

            ascii_art = ascii_art_dict.get(name, "")

            eq = inventory.Equipment(name_zh, description, amount, individual_value, object_type, stat_change_list, combo_object, ascii_art)
            equipment_dict[name] = eq
        return equipment_dict

equipment_data = load_equipment_from_csv()

# *-> 初始武器
basic_weapons = {
    "rusty_sword": equipment_data["rusty_sword"],
    "broken_dagger": equipment_data["broken_dagger"],
    "old_staff": equipment_data["old_staff"],
    "wood_bow": equipment_data["wood_bow"],
}

# *-> 初始护甲
novice_armor = equipment_data["novice_armor"]
old_robes = equipment_data["old_robes"]

# *-> 基本武器
long_sword = equipment_data["long_sword"]
dagger = equipment_data["dagger"]
staff = equipment_data["staff"]

# *-> 基础护甲
cloth_armor = equipment_data["cloth_armor"]
leather_armor = equipment_data["leather_armor"]
bronze_armor = equipment_data["bronze_armor"]
student_robes = equipment_data["student_robes"]

# *-> 基础护盾
wooden_shield = equipment_data["wooden_shield"]

# *-> 基础头盔
straw_hat = equipment_data["straw_hat"]

# *-> 基础护手
gloves_wraps = equipment_data["gloves_wraps"]

# *-> 基础护足
footrags = equipment_data["footrags"]

# *-> 基础饰品
copper_ring = equipment_data["copper_ring"]

# *-> 高级武器
war_hammer = equipment_data["war_hammer"]
zweihander = equipment_data["zweihander"]
sage_staff = equipment_data["sage_staff"]
sai = equipment_data["sai"]
long_bow = equipment_data["long_bow"]

# *-> 高级装甲
iron_armor = equipment_data["iron_armor"]
sage_tunic = equipment_data["sage_tunic"]
thief_armor = equipment_data["thief_armor"]

# *-> 高级护盾
bronze_shield = equipment_data["bronze_shield"]

# -> 高级头盔

# -> 高级护手

# -> 高级护足

# -> 高级饰品

# 消耗品
hp_potion = inventory.Potion("生命药水", "恢复70点生命值的药水", 1, 25, "consumable", "hp", 70)
mp_potion = inventory.Potion("法力药水", "恢复40点法力值的药水", 1, 25, "consumable", "mp", 40)

atk_small_gems = inventory.Jewel("攻击小宝石", "提升3点攻击力的宝石", 1, 150, "consumable", "atk", 3)
mat_small_gems = inventory.Jewel("魔攻小宝石", "提升3点魔法攻击力的宝石", 1, 150, "consumable", "mat", 3)
agi_small_gems = inventory.Jewel("敏捷小宝石", "提升3点敏捷的宝石", 1, 150, "consumable", "agi", 3)
crit_small_gems = inventory.Jewel("暴击小宝石", "提升1点暴击的宝石", 1, 125, "consumable", "crit", 1)

atk_gems = inventory.Jewel("攻击宝石", "提升5点攻击力的宝石", 1, 235, "consumable", "atk", 5)
mat_gems = inventory.Jewel("魔攻宝石", "提升5点魔法攻击力的宝石", 1, 235, "consumable", "mat", 5)
agi_gems = inventory.Jewel("敏捷宝石", "提升5点敏捷的宝石", 1, 235, "consumable", "agi", 5)
crit_gems = inventory.Jewel("暴击宝石", "提升3点暴击的宝石", 1, 310, "consumable", "crit", 3)

# 魔法书
grimoire_data = [
    ("魔法书：火球术", "记载了基础的火焰魔法，释放一颗灼热火球攻击敌人。", 1, 80, skills.spell_fire_ball),
    ("魔法书：神圣祝福", "古老教会的祝文，可恢复目标生命，带来圣光的治愈。", 1, 120, skills.spell_divine_blessing),
    ("魔法书：增强武器", "魔法附魔术式，可短时间内强化武器的攻击力。", 1, 120, skills.spell_enhance_weapon),
    ("魔法书: 地狱火", "中级火焰咒文，召唤烈焰吞噬所有敌人。", 1, 210, skills.spell_inferno),
    ("唤灵书: 骷髅召唤", "记载亡灵召唤术，可呼唤骷髅战士为你作战。", 1, 170, skills.spell_skeleton_summoning),
    ("唤灵书: 火精灵", "源自炎之古国的召唤术，召唤火焰元素协助作战。", 1, 215, skills.spell_fire_spirit_summoning),
]

grimoires = [
    inventory.Grimoire(n, d, a, v, "consumable", spell)
    for (n, d, a, v, spell) in grimoire_data
]

# 商店物品套装
rik_armor_shop_item_set = [
    long_sword,
    dagger,
    war_hammer,
    iron_armor,
    zweihander,
    cloth_armor,
    leather_armor,
    bronze_armor,
    sai,
    thief_armor,
    wooden_shield,
    bronze_shield,
    long_bow,
]

itz_magic_item_set = [
    staff,
    cloth_armor,
    hp_potion,
    mp_potion,
    sage_tunic,
    sage_staff,
    student_robes,
    *grimoires[:6],
    mat_small_gems,
]

anna_armor_shop_set = [
    cloth_armor,
    leather_armor,
    bronze_armor,
    student_robes,
    wooden_shield,
    straw_hat,
    gloves_wraps,
    footrags,
    copper_ring,
]

jack_weapon_shop_set = [
    basic_weapons["wood_bow"],
    long_sword,
    dagger,
    war_hammer,
]
