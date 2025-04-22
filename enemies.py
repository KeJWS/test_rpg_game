import csv
from random import randint
import random
from copy import deepcopy

from tools.dev_tools import debug_print

import combat

enemy_variants = {
    "elite": {
        "name_suffix": "•稀有",
        "stat_multiplier": 1.5,
        "xp_multiplier": 2.0,
        "gold_multiplier": 2.5,
    },
    "frenzy": {
        "name_suffix": "•狂暴",
        "stat_multiplier": {"atk": 2.0, "def": 0.5, "agi": 1.5},
        "xp_multiplier": 1.2,
        "gold_multiplier": 1.1,
    },
    "cursed": {
        "name_suffix": "•诅咒",
        "stat_multiplier": {"mdf": 1.2, "mat": 1.2, "luk": 0.8},
        "stat_bonus": {"mdf": 20, "luk": -10},
        "xp_multiplier": 1.7,
        "gold_multiplier": 1.2,
    },
    "shield": {
        "name_suffix": "•护盾",
        "stat_multiplier": {"max_hp": 1.5, "hp": 1.5, "def": 1.2, "mdf": 1.2, "agi": 0.5},
        "stat_bonus": {"def": 15, "mdf": 15, "agi": -5},
        "xp_multiplier": 2.1,
        "gold_multiplier": 1.5,
    },
}

def load_enemies_from_csv(filepath):
    enemies = {}
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stats = {key: int(row[key]) for key in (
                "max_hp", "max_mp", "atk", "def", "mat", "mdf", "agi", "luk", "crit", "anti_crit"
            )}
            stats["hp"] = stats["max_hp"]
            stats["mp"] = stats["max_mp"]

            xp = int(row["xp_reward"])
            gold = randint(int(row["gold_min"]), int(row["gold_max"]))
            level = row["level"]
            enemy = Enemy(row["name_zh"], stats, xp_reward=xp, gold_reward=gold, level=level)
            enemies[row["name"]] = enemy
    return enemies

class Enemy(combat.Battler):
    def __init__(self, name, stats, xp_reward, gold_reward, level) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.level = level
        self.original_stats = stats.copy()

    def clone(self, variant_name=None):
        cloned = Enemy(self.name, deepcopy(self.original_stats), self.xp_reward, self.gold_reward, self.level)
        if not variant_name:
            roll = random.random()
            if roll < 0.03:
                variant_name = "cursed"
            elif roll < 0.05:
                variant_name = "shield"
            elif roll < 0.08:
                variant_name = "frenzy"
            elif roll < 0.15:
                variant_name = "elite"

        if variant_name:
            apply_variant(cloned, variant_name)
        return cloned

def apply_variant(enemy, variant_name):
    variant = enemy_variants.get(variant_name)
    if not variant:
        return

    enemy.name += variant.get("name_suffix", "")
    
    # 属性乘数
    if "stat_multiplier" in variant:
        multiplier = variant["stat_multiplier"]
        if isinstance(multiplier, (int, float)):
            for stat in enemy.stats:
                enemy.stats[stat] = int(enemy.stats[stat] * multiplier)
        elif isinstance(multiplier, dict):
            for stat, value in multiplier.items():
                if stat in enemy.stats:
                    enemy.stats[stat] = int(enemy.stats[stat] * value)
    
    # 属性加成
    if "stat_bonus" in variant:
        for stat, value in variant["stat_bonus"].items():
            if stat in enemy.stats:
                enemy.stats[stat] += value

    # 奖励调整
    enemy.xp_reward = int(enemy.xp_reward * variant.get("xp_multiplier", 1.0))
    enemy.gold_reward = int(enemy.gold_reward * variant.get("gold_multiplier", 1.0))
    debug_print(f"应用变体：{enemy.name} -> {variant_name}")

def create_enemy_group(level, possible_enemies, enemy_quantity_for_level):
    valid_enemy_ids = [
        enemy_id for enemy_id, (low, high) in possible_enemies.items()
        if low <= level <= high
    ]

    # 确定敌人数量
    max_enemies = next(
        (enemy_quantity_for_level[max_level] for max_level in sorted(enemy_quantity_for_level) if level < max_level),
        1
    )
    num_enemies = random.randint(1, max_enemies)

    group = []
    for _ in range(num_enemies):
        enemy_id = random.choice(valid_enemy_ids)
        enemy = enemy_data[enemy_id].clone()  # 这里每个 enemy 都有自己独立的变体生成逻辑
        group.append(enemy)
    return group

enemy_data = load_enemies_from_csv("data/enemies.csv")

possible_enemies = {
    "slime": (1, 3),
    "imp": (1, 5),
    "golem": (1, 7),
}

# Boss 固定战
enemy_list_caesarus_bandit = [
    enemy_data["caesarus_bandit_leader"].clone(),
    enemy_data["bandit"].clone(),
    enemy_data["bandit"].clone(),
]

enemy_list_fight_against_slime = [
    enemy_data["giant_slime"].clone(),
    enemy_data["slime"].clone(),
    enemy_data["slime"].clone(),
    enemy_data["slime"].clone(),
]

enemy_list_fight_against_slime_king = [
    enemy_data["slime_king"].clone(),
    enemy_data["giant_slime"].clone(),
    enemy_data["giant_slime"].clone(),
]

enemy_list_fight_against_wolf_king = [
    enemy_data["wolf_king"].clone(),
    enemy_data["wolf"].clone(),
    enemy_data["wolf"].clone(),
    enemy_data["wolf"].clone(),
]
