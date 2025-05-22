from typing import List, Tuple

DEBUG = True
MONEY_MULTIPLIER = 1 # 金钱倍率
EXPERIENCE_RATE = 1 # 经验倍率

# 品质配置: 名称, 价格倍率, 属性倍率, 权重
QUALITY_CONFIG: List[Tuple[str, float, float, int]] = [
        ("生锈的", 0.5, 0.75, 25),
        ("普通的", 1.0, 1.0, 50),
        ("优质的", 2.2, 1.35, 13),
        ("魔法的", 4.5, 1.75, 9),
        ("传奇的", 12.0, 2.35, 3)
    ]

DEFAULT_EQUIPMENT_IMAGES = {
    "weapon": "img/equipments/default_weapon.png",
    "armor": "img/equipments/default_armor.png",
    "shield": "img/equipments/default_shield.png",
    "head": "img/equipments/default_head.png",
    "hand": "img/equipments/default_hand.png",
    "foot": "img/equipments/default_foot.png",
    "accessory": "img/equipments/default_accessory.png",
}

ENEMY_VARIANTS = {
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

POSSIBLE_ENEMIES = {
    "slime": (1, 3),
    "imp": (1, 5),
    "golem": (1, 7),
    "skeleton": (2, 9),
    "bandit": (2, 11),
    "goblin": (3, 12),
    "giant_slime": (4, 15),
    "lizard_scout": (4, 19),
}
