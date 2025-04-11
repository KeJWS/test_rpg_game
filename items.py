import inventory
import csv
import ast

def load_equipment_from_csv(filepath="data/equipments.csv"):
    equipment_dict = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            name_zh = row["name_zh"]
            description = row["description"]
            amount = int(row["amount"])
            individual_value = int(row["individual_value"])
            object_type = row["object_type"]
            # 用 ast.literal_eval 安全地解析字典字符串
            stat_change_list = ast.literal_eval(row["stat_change_list"])
            eq = inventory.Equipment(name_zh, description, amount, individual_value, object_type, stat_change_list)
            equipment_dict[name] = eq
        return equipment_dict

equipment_data = load_equipment_from_csv()

# 初始物品
# -> 初始武器
rusty_sword = equipment_data["rusty_sword"]
broken_dagger = equipment_data["broken_dagger"]
old_staff = equipment_data["old_staff"]
# -> 初始护甲
novice_armor = equipment_data["novice_armor"]
old_robes = equipment_data["old_robes"]

# 基本物品
# -> 基本武器
long_sword = equipment_data["long_sword"]
dagger = equipment_data["dagger"]
staff = equipment_data["staff"]

# -> 基础护甲
cloth_armor = inventory.Equipment('布甲', '', 1, 20, 'armor', {'max_hp' : 2, 'def' : 2})
bronze_armor = equipment_data["bronze_armor"]
student_robes = equipment_data["student_robes"]

# -> 基础护盾
wooden_shield = equipment_data["wooden_shield"]

# -> 基础头盔
straw_hat = equipment_data["straw_hat"]

# -> 基础护手
gloves_wraps = equipment_data["gloves_wraps"]

# -> 基础护足
footrags = equipment_data["footrags"]

# -> 基础饰品
copper_ring = equipment_data["copper_ring"]

# 高级物品
# -> 高级武器
war_hammer = inventory.Equipment('战锤', '', 1, 62, 'weapon', {'atk' : 13, 'agi' : -2})
zweihander = equipment_data["zweihander"]
sage_staff = equipment_data["sage_staff"]
sai = equipment_data["sai"]

# -> 高级装甲
iron_armor = inventory.Equipment('铁甲', '', 1, 102, 'armor', {'max_hp' : 8, 'def' : 10})
sage_tunic = equipment_data["sage_tunic"]
thief_armor = equipment_data["thief_armor"]

# -> 高级头盔
helmet_bronze = equipment_data["helmet_bronze"]

# -> 高级护手
gauntlets_larmor = equipment_data["gauntlets_larmor"]

# -> 高级护足
boots_plate = equipment_data["boots_plate"]

# -> 高级饰品
ring_of_power = equipment_data["ring_of_power"]
ring_of_magic = equipment_data["ring_of_magic"]

# 消耗品
hp_potion = inventory.Potion('生命药水', 'a', 1, 10, 'consumable', 'hp', 30)
mp_potion = inventory.Potion('法力药水', 'a', 1, 10, 'consumable', 'mp', 15)

# 商店物品套装

rik_armor_shop_item_set = [
    long_sword,
    dagger,
    war_hammer,
    iron_armor,
    zweihander,
    cloth_armor,
    bronze_armor,
    sai,
    thief_armor,
]

itz_magic_item_set = [
    staff,
    cloth_armor,
    hp_potion,
    mp_potion,
    sage_tunic,
    sage_staff,
    student_robes,
]
