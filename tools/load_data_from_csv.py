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
            amount = 1
            individual_value = int(row["individual_value"]) if row["individual_value"].strip() else 0
            stat = row["stat"]
            amount_to_change = int(row["amount_to_change"]) if row["amount_to_change"].strip() else 0
            jewel = item.Jewel(name_zh, description, amount, individual_value, stat, amount_to_change)
            jewel_dict[name] = jewel

        debug_print(f"从 CSV 加载数据，共加载 {len(jewel_dict)} 种宝石")
        return jewel_dict

def load_food_from_csv(filepath="data/csv_data/food.csv"):
    food_dict = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            name_zh = row["name_zh"]
            description = row["description"]
            amount = 1
            individual_value = int(row["individual_value"]) if row["individual_value"].strip() else 0
            hunger_restore = int(row["hunger_restore"]) if row["hunger_restore"].strip() else 0
            hp_restore = int(row["hp_restore"]) if row["hp_restore"].strip() else 0
            mp_restore = int(row["mp_restore"]) if row["mp_restore"].strip() else 0
            food = item.Food(name_zh, description, amount, individual_value, hunger_restore, hp_restore, mp_restore)
            food_dict[name] = food

        debug_print(f"从 CSV 加载数据，共加载 {len(food_dict)} 种食物")
        return food_dict
