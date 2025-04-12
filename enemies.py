import csv
from random import randint
import combat

'''
敌人等级定义，专门用于自定义统计和奖励。
'''

def load_enemies_from_csv(filepath):
    enemies = {}
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stats = {
                "max_hp": int(row["max_hp"]),
                "hp": int(row["max_hp"]),
                "max_mp": int(row["max_mp"]),
                "mp": int(row["max_mp"]),
                "atk": int(row["atk"]),
                "def": int(row["def"]),
                "mat": int(row["mat"]),
                "mdf": int(row["mdf"]),
                "agi": int(row["agi"]),
                "luk": int(row["luk"]),
                "crit": int(row["crit"])
            }
            xp = int(row["xp_reward"])
            gold = randint(int(row["gold_min"]), int(row["gold_max"]))
            enemy = combat.Enemy(row["name_zh"], stats, xp_reward=xp, gold_reward=gold)
            enemies[row["name"]] = enemy
    return enemies

enemy_data = load_enemies_from_csv("data/enemies.csv")

# 可能的敌人：（出现的最低玩家等级，出现的最高玩家等级）
possible_enemies = {
    "slime": (1, 3),
    "imp": (1, 4),
    "golem": (2, 7),
    "skeleton": (2, 10),
    "giant_slime": (3, 100),
    "bandit": (4, 100)
}

# 固定战斗敌人
enemy_list_caesarus_bandit = [enemy_data["caesarus_bandit_leader"].clone(), enemy_data["bandit"].clone(), enemy_data["bandit"].clone()]
