"""
地区工厂模块，负责创建和初始化游戏世界中的各个地区。

该模块包含了从数据字典创建Region对象的工厂函数，以及各种预定义的
事件映射和任务映射。提供了标准化的地区创建机制，使游戏地图初始化
过程更加一致和可维护。
"""

import random
from typing import Dict, List, Any

import events
import enemies
from data import items_data
from data import DIALOGUE
from data import equipment_data
from world import quest
from world.map import Region

SHOP_EVENTS = {
    "shop_jack_weapon": events.ShopEvent(
        "杰克的武器店", False,
        DIALOGUE['jack_shop']['encounter'], DIALOGUE['jack_shop']['enter'],
        DIALOGUE['jack_shop']['talk'], DIALOGUE['jack_shop']['exit'],
        items_data.jack_weapon_shop_set
    ),
    "shop_anna_armor": events.ShopEvent(
        "安娜的防具店", False,
        DIALOGUE['anna_shop']['encounter'], DIALOGUE['anna_shop']['enter'],
        DIALOGUE['anna_shop']['talk'], DIALOGUE['anna_shop']['exit'],
        items_data.anna_armor_shop_set
    ),
    "mary_food_stall": events.ShopEvent(
        "玛丽的小吃摊", False,
        DIALOGUE['mary_shop']['encounter'], DIALOGUE['mary_shop']['enter'],
        DIALOGUE['mary_shop']['talk'], DIALOGUE['mary_shop']['exit'],
        items_data.mary_food_stall_set
    ),
    "shop_rik_armor": events.ShopEvent(
        "里克的盔甲店", False,
        DIALOGUE['rik_shop']['encounter'], DIALOGUE['rik_shop']['enter'],
        DIALOGUE['rik_shop']['talk'], DIALOGUE['rik_shop']['exit'],
        items_data.rik_armor_shop_item_set
    ),
    "shop_lok_armor": events.ShopEvent(
        "青铜匠武具店", False,
        DIALOGUE['lok_shop']['encounter'], DIALOGUE['lok_shop']['enter'],
        DIALOGUE['lok_shop']['talk'], DIALOGUE['lok_shop']['exit'],
        items_data.lok_armor_shop_item_set
    ),
    "shop_itz_magic": events.ShopEvent(
        "伊兹的魔法店", False,
        DIALOGUE['itz_shop']['encounter'], DIALOGUE['itz_shop']['enter'],
        DIALOGUE['itz_shop']['talk'], DIALOGUE['itz_shop']['exit'],
        items_data.itz_magic_item_set
    ),
    "mysterious_businessman": events.ShopEvent(
        "神秘商人", False,
        DIALOGUE['mysterious_shop']['encounter'], DIALOGUE['mysterious_shop']['enter'],
        DIALOGUE['mysterious_shop']['talk'], DIALOGUE['mysterious_shop']['exit'],
        items_data.rik_armor_shop_item_set
    ),
}

COMBAT_EVENTS = {
    "fight_against_slime_combat": events.FixedCombatEvent("史莱姆狩猎", enemies.giant_slime_lists),
    "fight_against_slime_king_combat": events.FixedCombatEvent("史莱姆之王", enemies.slime_king_lists),
    "caesarus_bandit_combat": events.FixedCombatEvent("凯撒鲁斯与他的强盗", enemies.caesarus_bandit_lists),
    "wolf_king_combat": events.FixedCombatEvent("夜行狼王", enemies.wolf_king_lists),
}

OTHER_EVENTS = {
    "inn_event": events.InnEvent(
        "客栈", DIALOGUE['inn_event']['encounter'], DIALOGUE['inn_event']['success'],
        DIALOGUE['inn_event']['fail'], DIALOGUE['inn_event']['refuse'], 160, 25
    ),
    "heal_medussa_statue": events.HealingEvent(
        "美杜莎雕像", DIALOGUE['medussa_statue']['encounter'], DIALOGUE['medussa_statue']['success'],
        DIALOGUE['medussa_statue']['fail'], DIALOGUE['medussa_statue']['refuse'], 75, False, 90
    ),

    "find_coins": events.SimpleEvent("发现金币", events.find_coins_effect),
    "admire_scenery": events.SimpleEvent("欣赏风景", events.admire_scenery_effect),
    "friendly_villager": events.SimpleEvent("友好村民", events.friendly_villager_effect),
    "find_herb": events.SimpleEvent("发现草药", events.find_herb_effect),
    "rest_spot": events.SimpleEvent("休息处", events.rest_spot_effect),

    "hidden_chest_forest": events.HiddenChestEvent("雾林装备宝箱", random.choice(["long_sword", "dagger", "fire_staff"])),
    "hidden_chest_mountain": events.HiddenChestEvent("龙脊山装备宝箱", random.choice(["sword_bronze", "sai", "amulet_of_health"])),
    "hidden_chest_swamp": events.HiddenChestEvent("迷雾沼泽装备宝箱", random.choice(["hunting_knife", "ring_of_power", "ring_of_magic", "mana_charm", "bronze_mace"])),
}

EVENT_MAPPING: Dict[str, Any] = {}
EVENT_MAPPING.update(SHOP_EVENTS)
EVENT_MAPPING.update(COMBAT_EVENTS)
EVENT_MAPPING.update(OTHER_EVENTS)

QUEST_MAPPING: Dict[str, quest.Quest] = {
    "hunting_slimes": quest.Quest(
        "史莱姆狩猎",
        DIALOGUE['kill_slimes']['text'],
        DIALOGUE['kill_slimes']['mayor_text'],
        50, 50, equipment_data["zweihander"], EVENT_MAPPING["fight_against_slime_combat"], 3
    ),
    "slime_king": quest.Quest(
        "史莱姆之王",
        DIALOGUE['slime_king']['text'],
        DIALOGUE['slime_king']['itz_text'],
        170, 230, equipment_data["long_bow"], EVENT_MAPPING["fight_against_slime_king_combat"], 9
    ),
    "caesarus_bandit": quest.Quest(
        "凯撒鲁斯与他的强盗",
        DIALOGUE['caesarus_bandit']['text'],
        DIALOGUE['caesarus_bandit']['rik_text'],
        150, 150, None, EVENT_MAPPING["caesarus_bandit_combat"], 5
    ),
    "wolf_king": quest.Quest(
        "夜行狼王",
        DIALOGUE['wolf_king']['text'],
        DIALOGUE['wolf_king']['mira_text'],
        350, 700, equipment_data["wolf_king_proof"], EVENT_MAPPING["wolf_king_combat"], 13
    ),
    "wolf_hide_quest": quest.Quest(
        "收集狼皮",
        "猎人需要 5 张狼皮制作斗篷，请前往森林击杀野狼。",
        "嘿, 冒险者, 你愿意帮我收集狼皮吗? 我需要5张!",
        300, 300, None, None, 5, {"狼皮": 5}
    ),
    "slime_gels_quest": quest.Quest(
        "收集凝胶",
        "需要 5 份凝胶",
        "冒险者，请协助收集 5 份凝胶资源，感激不尽。",
        100, 100, None, None, 1, {"凝胶": 5}
    )
}

def load_region_from_dict(data: dict, ascii_art_dict: dict) -> Region:
    """
    从数据字典创建一个Region对象。

    解析提供的数据字典，提取地区的各种属性，并使用全局的事件映射和任务映射
    转换事件和任务的引用名称为实际对象。这是实现数据驱动地区创建的核心函数。

    参数:
        data: 包含地区数据的字典，通常从JSON文件加载
        ascii_art_dict: ASCII艺术字典，用于获取地区的视觉表示

    返回:
        Region: 新创建的地区对象
    """
    name = data.get("name", "未知地区")
    description = data.get("description", "")
    danger_level = data.get("danger_level", 1)
    possible_enemies = data.get("possible_enemies", {})

    def map_event_list(key: str) -> List[Any]:
        return [EVENT_MAPPING.get(ev_name) for ev_name in data.get(key, []) if ev_name in EVENT_MAPPING]

    shop_events = map_event_list("shop_events")
    heal_events = map_event_list("heal_events")
    special_events = map_event_list("special_events")
    quests = [QUEST_MAPPING[qname] for qname in data.get("quests", []) if qname in QUEST_MAPPING]
    ascii_art = ascii_art_dict.get(data.get("ascii_art_key", ""), "")

    return Region(
        name=name,
        description=description,
        danger_level=danger_level,
        possible_enemies=possible_enemies,
        shop_events=shop_events,
        heal_events=heal_events,
        special_events=special_events,
        quests=quests,
        ascii_art=ascii_art
    )

def create_redflame_canyon(ascii_art_dict):
    """
    创建赤焰峡谷地区。

    初始化并返回一个表示赤焰峡谷的Region对象，设置其名称、描述、
    危险等级和ASCII艺术表示。这是一个火元素主题的地区，具有高温和
    火系魔物的特性。

    参数:
        ascii_art_dict: ASCII艺术字典，用于获取地区的视觉表示

    返回:
        Region: 表示赤焰峡谷的地区对象
    """
    fire_canyon_enemies = {}
    redflame_canyon = Region(
        name="赤焰峡谷",
        description="灼热干裂的峡谷, 有火元素和岩浆魔物出没。高温会持续削弱你的体力, 谨慎前行。",
        danger_level=3,
        possible_enemies=fire_canyon_enemies,
        shop_events=[],
        heal_events=[],
        special_events=[],
        quests=[],
        ascii_art=ascii_art_dict.get("赤焰峡谷", "")
    )
    return redflame_canyon

def create_snowlands(ascii_art_dict):
    """
    创建雪之边境地区。

    初始化并返回一个表示雪之边境的Region对象，设置其名称、描述、
    危险等级和ASCII艺术表示。这是一个冰雪主题的地区，具有极寒和
    视线受限的特性。
    """
    snowland_enemies = {}
    snowlands = Region(
        name="雪之边境",
        description="一望无际的雪原, 雪怪和冰霜精灵在这片冰天雪地中游荡。\n风雪会干扰视线, 也会影响技能释放。",
        danger_level=3,
        possible_enemies=snowland_enemies,
        shop_events=[],
        heal_events=[],
        special_events=[],
        quests=[],
        ascii_art=ascii_art_dict.get("雪之边境", "")
    )
    return snowlands

def create_forgotten_ruins(ascii_art_dict):
    """
    创建遗忘遗迹地区。

    初始化并返回一个表示遗忘遗迹的Region对象，设置其名称、描述、
    危险等级和ASCII艺术表示。这是一个古代遗迹主题的地区，具有
    古老机关和守卫魔像的特性。
    """
    ruins_enemies = {}
    forgotten_ruins = Region(
        name="遗忘遗迹",
        description="一座尘封千年的古老遗迹, 据说隐藏着古代文明的魔导科技。\n机关重重, 还有被封印的魔像在此守卫。",
        danger_level=4,
        possible_enemies=ruins_enemies,
        shop_events=[],
        heal_events=[],
        special_events=[],
        quests=[],
        ascii_art=ascii_art_dict.get("遗忘遗迹", "")
    )
    return forgotten_ruins
