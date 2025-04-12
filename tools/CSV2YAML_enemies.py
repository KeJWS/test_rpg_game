import csv
import yaml

# **1️⃣ 读取 CSV 文件并转换为 YAML 格式**
with open("data/enemies.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    equipment_list = []

    for row in reader:

        item = {
            "id": int(row["id"]),
            "name": row["name"],
            "name_zh": row["name_zh"],
            "max_hp": int(row["max_hp"]),
            "max_mp": int(row["max_mp"]),
            "atk": int(row["atk"]),
            "def": int(row["def"]),
            "mat": int(row["mat"]),
            "mdf": int(row["mdf"]),
            "agi": int(row["agi"]),
            "luk": int(row["luk"]),
            "crit": int(row["crit"]),
            "xp_reward": int(row["xp_reward"]),
            "gold_min": int(row["gold_min"]),
            "gold_max": int(row["gold_max"]),
        }
        equipment_list.append(item)

# **2️⃣ 设定 YAML 统一的字段顺序**
field_order = ["id", "name", "name_zh", "max_hp", "max_mp", "atk", "def", "mat", "mdf", "agi", "luk", "crit", "xp_reward", "gold_min", "gold_max"]
sorted_equipment = [{key: item.get(key, None) for key in field_order} for item in equipment_list]

# **3️⃣ 生成最终的 YAML 数据**
# yaml_data = {"Equipment": sorted_equipment}

# **4️⃣ 写入 YAML 文件**
with open("enemies.yaml", "w", encoding="utf-8") as file:
    yaml.dump(sorted_equipment, file, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("✅ CSV 已成功转换并整理为 YAML!")
