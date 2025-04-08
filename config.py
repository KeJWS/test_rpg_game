# config.py
"""游戏配置管理模块"""
import json
import os

DEFAULT_CONFIG = {
    "combat": {
        "base_hit_chance": 90,
        "crit_rates": {
            "1.5": 50,
            "2.0": 30,
            "2.5": 15,
            "3.0": 5
        },
        "damage_variation": 0.2,  # 伤害浮动范围 ±20%
        "defense_reduction": 0.5  # 防御减伤比例
    },
    "progression": {
        "exp_rate": 1.0,
        "level_up_exp_multiplier": 1.5,
        "stat_increase_per_level": 1
    },
    "economy": {
        "money_multiplier": 1.0,
        "shop_sell_ratio": 0.7  # 商店回购价格比例
    }
}

def load_config():
    """加载游戏配置，如果不存在则创建默认配置"""
    config_path = "game_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("配置文件损坏，使用默认配置")
            return DEFAULT_CONFIG
    else:
        # 创建默认配置文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG

# 全局配置对象
CONFIG = load_config()