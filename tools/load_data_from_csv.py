import csv

import others.item as item
from tools.dev_tools import debug_print

# 宝石数据加载
def load_jewel_from_csv(filepath="data/csv_data/jewels.csv"):
    jewel_dict = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            name_zh = row["name_zh"]
            description = row["description"]
            amount = int(row["amount"]) if row["amount"].strip() else 1
            individual_value = int(row["individual_value"])
            stat = row["stat"]
            amount_to_change = int(row["amount_to_change"])
            jewel = item.Jewel(name_zh, description, amount, individual_value, stat, amount_to_change)
            jewel_dict[name] = jewel

        debug_print(f"从 CSV 加载装备数据，共加载 {len(jewel_dict)} 种宝石")
        return jewel_dict
