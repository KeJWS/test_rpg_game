import yaml
import csv

# 1. 读取 YAML 文件
with open("enemies.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

# 2. 提取 "Equipment" 数据
# equipment_data = data.get("Equipment", [])

# 3. 写入 CSV 文件
with open("enemies.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # 写入表头
    headers = ["id", "name", "name_zh", "max_hp", "max_mp", "atk", "def", "mat", "mdf", "agi", "luk", "crit", "xp_reward", "gold_min", "gold_max"]
    writer.writerow(headers)

    # 写入数据
    for item in data:
        writer.writerow([
            item["id"], item["name"], item["name_zh"], item["max_hp"], 
            item["max_mp"], item["atk"], item["def"], item["mat"], item["mdf"], item["agi"], item["luk"], item["crit"],
            item["xp_reward"], item["gold_min"], item["gold_max"]
        ])

print("✅ YAML 已成功转换为 CSV!")
