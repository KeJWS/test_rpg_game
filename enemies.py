"""
敌人系统模块，处理游戏中敌人的创建、属性管理和战斗行为决策。

该模块提供了从CSV文件加载敌人数据、创建敌人实例、应用不同敌人变体、
以及生成敌人战斗组合的功能。同时实现了敌人在战斗中的行为决策逻辑。
"""

from data.constants import POSSIBLE_ENEMIES
import csv
import random
from copy import deepcopy

from core import battler
from data.constants import ENEMY_VARIANTS
from mods.dev_tools import debug_print

def load_enemies_from_csv(filepath):
    """
    从CSV文件加载敌人数据。

    解析指定CSV文件中的敌人数据，创建对应的Enemy对象，
    并设置其属性、奖励、掉落物品和技能。

    参数:
        filepath: CSV文件路径

    返回:
        dict: 以敌人ID为键，Enemy对象为值的字典
    """
    import data.items_data as items_data
    from data.skills_data import SPELL_REGISTRY

    enemies = {}
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stats = {key: int(row[key]) if row[key].strip() else 0 for key in (
                "max_hp", "max_mp", "atk", "def", "mat", "mdf", "agi", "luk", "crit", "anti_crit"
            )}
            stats["hp"] = stats["max_hp"]
            stats["mp"] = stats["max_mp"]

            xp = int(row["xp_reward"]) if row["xp_reward"].strip() else 0
            gold = random.randint(int(row["gold_min"]) if row["gold_min"].strip() else 0, int(row["gold_max"]) if row["gold_max"].strip() else 0)
            level = row["level"]

            drop_items = []
            drop_field = row.get("drop_items", "").strip()
            if drop_field:
                for part in drop_field.split(","):
                    if "x" in part:
                        item_name, count = part.split("x")
                        item = items_data.item_factory(item_name.strip(), int(count))
                        if item:
                            drop_items.append(item)

            enemy = Enemy(row["name_zh"], stats, xp_reward=xp, gold_reward=gold, level=level, drop_items=drop_items)

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
            assign_enemy_action_weights(enemy, row["name"])
            enemies[row["name"]] = enemy
        debug_print(f"从 CSV 加载敌人数据, 共加载 {len(enemies)} 项数据")
    return enemies

def assign_enemy_action_weights(enemy, enemy_type):
    """
    根据敌人类型分配行动权重。

    为不同类型的敌人分配攻击、防御和技能使用的概率权重，
    以影响其在战斗中的行为模式。

    参数:
        enemy: 要设置行动权重的Enemy对象
        enemy_type: 敌人类型标识符
    """
    if "slime" in enemy_type:
        if "giant" in enemy_type:
            enemy.action_weights = {"attack": 60, "defend": 10, "spell": 30}

    elif "skeleton" in enemy_type:
        enemy.action_weights = {"attack": 65, "defend": 15, "spell": 20}

    elif "golem" in enemy_type:
        enemy.action_weights = {"attack": 55, "defend": 25, "spell": 20}

    elif "imp" in enemy_type:
        enemy.action_weights = {"attack": 60, "defend": 5, "spell": 35}

    elif "bandit" in enemy_type:
        if "leader" in enemy_type:
            enemy.action_weights = {"attack": 45, "defend": 20, "spell": 35}


class Enemy(battler.Battler):
    """
    敌人类，表示游戏中可战斗的对手角色。

    继承自Battler基类，添加了敌人特有的属性如经验奖励、金币奖励、
    物品掉落和行动决策逻辑。
    """

    def __init__(self, name, stats, xp_reward, gold_reward, level, drop_items=None) -> None:
        """
        初始化敌人实例。

        设置敌人的基本属性、战斗数值、奖励和默认行动权重。

        参数:
            name: 敌人名称
            stats: 包含各项战斗属性的字典
            xp_reward: 击败后获得的经验值
            gold_reward: 击败后获得的金币
            level: 敌人等级
            drop_items: 击败后可能掉落的物品列表
        """
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.level = level
        self.original_stats = stats.copy()
        self.action_weights = {
            "attack": 60,
            "defend": 10,
            "spell": 30
        }
        self.drop_items = drop_items or []

    def clone(self, variant_name=None):
        """
        创建敌人的克隆实例，可选择应用变体效果。

        复制当前敌人的所有属性和状态，并根据指定或随机选择的变体
        修改其属性。

        参数:
            variant_name: 要应用的变体名称，若为None则随机选择

        返回:
            Enemy: 敌人的新实例，可能包含变体效果
        """
        cloned = Enemy(self.name, deepcopy(self.original_stats), self.xp_reward, self.gold_reward, self.level, drop_items=deepcopy(self.drop_items))
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
        """
        决定敌人在战斗中的下一步行动。

        基于当前战斗状态和预设的行动权重，决定是攻击、防御还是使用技能，
        并选择适当的目标。

        参数:
            allies: 可选择的目标列表（通常是玩家角色或队伍）

        返回:
            dict: 包含行动类型和目标的行动描述字典
        """
        # 拷贝当前行为权重
        weights = self.action_weights.copy()

        if self.stats["hp"] < self.stats["max_hp"] * 0.3:
            weights["defend"] = 35
            weights["attack"] = 30
            weights["spell"] = 35

        usable_spells = [spell for spell in self.spells if self.stats["mp"] >= spell.cost]

        if not usable_spells:
            weights["spell"] = 0
            total = weights["attack"] + weights["defend"]
            weights["attack"] = round(weights["attack"] / total * 100)
            weights["defend"] = round(weights["defend"] / total * 100)

        action_type = random.choices(
            ["attack", "defend", "spell"], 
            weights=[weights["attack"], weights["defend"], weights["spell"]]
        )[0]

        debug_print(f"{self.name} 当前 MP: {self.stats['mp']}, 可用法术: {[s.name for s in usable_spells]}")

        if action_type == "attack":
            return {"type": "attack", "target": random.choice(allies)}
        elif action_type == "defend":
            return {"type": "defend"}
        else:
            spell = random.choice(usable_spells)
            return {"type": "spell", "spell": spell, "target": None}


def apply_variant(enemy, variant_name):
    """
    对敌人应用指定的变体效果。

    根据变体定义修改敌人的名称、属性和奖励，使其具有特殊特性。

    参数:
        enemy: 要应用变体的Enemy对象
        variant_name: 变体名称，必须在ENEMY_VARIANTS中定义
    """
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
    """
    根据玩家等级创建敌人组合。

    基于玩家等级和可能的敌人池，随机生成适合挑战难度的敌人组合。

    参数:
        level: 玩家等级
        possible_enemies: 可选敌人池及其适用等级范围
        enemy_quantity_for_level: 不同等级段的敌人数量上限

    返回:
        list: 包含Enemy对象的敌人组合
    """
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

possible_enemies = POSSIBLE_ENEMIES

# Boss 固定战
# TODO 每杀死一个, 游戏中便减少一个
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
