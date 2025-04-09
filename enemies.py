import csv
from random import randint
import combat

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
            enemy = combat.Enemy(row["name"], stats, xp_reward=xp, gold_reward=gold)
            enemies[row["name"]] = enemy
    return enemies

enemy_data = load_enemies_from_csv("data/enemies.csv")

possible_enemies = {
    "小鬼": (1, 3),
    "魔像": (2, 4),
    "巨型史莱姆": (3, 100)
}
