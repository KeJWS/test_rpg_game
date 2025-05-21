"""
CSV数据加载模块，用于从CSV文件中加载游戏数据。

该模块提供了从CSV文件加载各种游戏数据的功能，如宝石和食物。
通过读取格式化的CSV文件，将数据转换为游戏中可用的对象实例。
"""

import csv

import others.item as item
from tools.dev_tools import debug_print

def load_jewel_from_csv(filepath="data/csv_data/jewels.csv"):
    """
    从CSV文件中加载宝石数据。

    读取指定CSV文件，解析每行数据并创建相应的Jewel对象。
    CSV文件应包含宝石的名称、描述、价值、影响的属性和属性变化量等信息。

    参数:
        filepath: CSV文件路径，默认为"data/csv_data/jewels.csv"

    返回:
        dict: 以宝石英文名为键、Jewel对象为值的字典
    """
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
    """
    从CSV文件中加载食物数据。

    读取指定CSV文件，解析每行数据并创建相应的Food对象。
    CSV文件应包含食物的名称、描述、价值、恢复的饥饿值、生命值和魔法值等信息。

    参数:
        filepath: CSV文件路径，默认为"data/csv_data/food.csv"

    返回:
        dict: 以食物英文名为键、Food对象为值的字典
    """
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
