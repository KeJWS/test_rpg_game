import csv
import random
from copy import deepcopy

from core import battler
from data.constants import ENEMY_VARIANTS
from tools.dev_tools import debug_print


def load_enemies_from_csv(filepath):
    from skills import SPELL_REGISTRY
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
            gold = random.randint(int(row["gold_min"]), int(row["gold_max"]))
            level = row["level"]
            enemy = Enemy(row["name_zh"], stats, xp_reward=xp, gold_reward=gold, level=level)

            spell_names = row.get("spells", "").strip()
            if spell_names:
                for spell_name in spell_names.split(","):
                    spell_name = spell_name.strip()
                    spell_object = SPELL_REGISTRY.get(spell_name)
                    if spell_object:
                        enemy.spells.append(spell_object)
                    else:
                        debug_print(f"[警告] 技能 `{spell_name}` 不存在于 SPELL_REGISTRY 中")
            else:
                default_spell = SPELL_REGISTRY.get("enemy_fireball")
                if default_spell:
                    enemy.spells.append(default_spell)
            enemies[row["name"]] = enemy
    return enemies


class Enemy(battler.Battler):
    def __init__(self, name, stats, xp_reward, gold_reward, level) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.level = level
        self.original_stats = stats.copy()
        self.action_weights = {
            "attack": 60,
            "defend": 15,
            "spell": 25
        }

    def clone(self, variant_name=None):
        cloned = Enemy(self.name, deepcopy(self.original_stats), self.xp_reward, self.gold_reward, self.level)
        cloned.spells = self.spells.copy()
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

    def decide_action(self, allies):
        """敌人AI决策"""
        if self.stats["hp"] < self.stats["max_hp"] * 0.3:
            self.action_weights["defend"] = 35
            self.action_weights["attack"] = 35
            self.action_weights["spell"] = 30

        usable_spells = [spell for spell in self.spells if self.stats["mp"] >= spell.cost]

        if not usable_spells:
            self.action_weights["spell"] = 0
            total = self.action_weights["attack"] + self.action_weights["defend"]
            self.action_weights["attack"] = round(self.action_weights["attack"] / total * 100)
            self.action_weights["defend"] = round(self.action_weights["defend"] / total * 100)

        action_type = random.choices(
            ["attack", "defend", "spell"], 
            weights=[self.action_weights["attack"], self.action_weights["defend"], self.action_weights["spell"]]
        )[0]

        if len(self.spells) == 0 or self.stats["mp"] < min([s.cost for s in self.spells] or [999]):
            self.action_weights["spell"] = 0
            total = self.action_weights["attack"] + self.action_weights["defend"]
            self.action_weights["attack"] = round(self.action_weights["attack"] / total * 100)
            self.action_weights["defend"] = round(self.action_weights["defend"] / total * 100)

        if action_type == "attack":
            return {"type": "attack", "target": random.choice(allies)}
        elif action_type == "defend":
            return {"type": "defend"}
        else:
            spell = random.choice(usable_spells)
            return {"type": "spell", "spell": spell, "target": None}

def apply_variant(enemy, variant_name):
    variant = ENEMY_VARIANTS.get(variant_name)
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

enemy_data = load_enemies_from_csv("data/csv_data/enemies.csv")

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
