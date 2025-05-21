"""
地区工厂模块，负责创建和初始化游戏世界中的各个地区。

该模块包含了从数据字典创建Region对象的工厂函数，以及各种预定义的
事件映射和任务映射。提供了标准化的地区创建机制，使游戏地图初始化
过程更加一致和可维护。
"""

import random
import events, enemies, items
from world import quest
import data.event_text as ev
from world.map import Region

event_mapping = {
    "shop_jack_weapon": events.ShopEvent("杰克的武器店", False, ev.jack_weapon_shop_encounter, ev.jack_weapon_shop_enter, \
                            ev.jack_weapon_shop_talk, ev.jack_weapon_shop_exit, items.jack_weapon_shop_set),
    "shop_anna_armor": events.ShopEvent("安娜的防具店", False, ev.anna_armor_shop_encounter, ev.anna_armor_shop_enter, \
                            ev.anna_armor_shop_talk, ev.anna_armor_shop_exit, items.anna_armor_shop_set),
    "mary_food_stall": events.ShopEvent("玛丽的小吃摊", False, ev.mary_food_stall_encounter, ev.mary_food_stall_enter, \
                            ev.mary_food_stall_talk, ev.mary_food_stall_exit, items.mary_food_stall_set),
    "inn_event": events.InnEvent("客栈", ev.inn_event_encounter, ev.inn_event_success, ev.inn_event_fail, ev.inn_event_refuse, 150, 25),
    "heal_medussa_statue": events.HealingEvent("美杜莎雕像", ev.medussa_statue_encounter, ev.medussa_statue_success, \
                            ev.medussa_statue_fail, ev.medussa_statue_refuse, 75, False, 90),
    "fight_against_slime_combat": events.FixedCombatEvent("史莱姆狩猎", enemies.enemy_list_fight_against_slime),
    "fight_against_slime_king_combat": events.FixedCombatEvent("史莱姆之王", enemies.enemy_list_fight_against_slime_king),
    "shop_rik_armor": events.ShopEvent("里克的盔甲店", False, ev.rik_armor_shop_encounter, ev.rik_armor_shop_enter, \
                            ev.rik_armor_shop_talk, ev.rik_armor_shop_exit, items.rik_armor_shop_item_set),
    "shop_lok_armor": events.ShopEvent("青铜匠武具店", False, ev.lok_armor_shop_encounter, ev.lok_armor_shop_enter, \
                            ev.lok_armor_shop_talk, ev.lok_armor_shop_exit, items.lok_armor_shop_item_set),
    "caesarus_bandit_combat": events.FixedCombatEvent("凯撒鲁斯与他的强盗", enemies.enemy_list_caesarus_bandit),
    "shop_itz_magic": events.ShopEvent("伊兹的魔法店", False, ev.itz_magic_encounter, ev.itz_magic_enter, ev.itz_magic_talk, \
                            ev.itz_magic_exit, items.itz_magic_item_set),
    "wolf_king_combat": events.FixedCombatEvent("夜行狼王", enemies.enemy_list_fight_against_wolf_king),

    "find_coins": events.SimpleEvent("发现零钱", events.find_coins),
    "admire_scenery": events.SimpleEvent("欣赏美景", events.admire_scenery),
    "friendly_villager": events.SimpleEvent("村民物资", events.friendly_villager),
    "find_herb": events.SimpleEvent("找到草药", events.find_herb),
    "rest_spot": events.SimpleEvent("短暂休息", events.rest_spot),

    "mysterious_businessman": events.ShopEvent("神秘商人", False, ev.mysterious_businessman_encounter, ev.mysterious_businessman_enter, \
                            ev.mysterious_businessman_talk, ev.mysterious_businessman_exit, items.rik_armor_shop_item_set),

    "hidden_chest_forest": events.HiddenChestEvent("雾林装备宝箱", random.choice(["long_sword", "dagger", "fire_staff"])),
    "hidden_chest_mountain": events.HiddenChestEvent("龙脊山装备宝箱", random.choice(["sword_bronze", "sai", "amulet_of_health"])),
    "hidden_chest_swamp": events.HiddenChestEvent("迷雾沼泽装备宝箱", random.choice(["hunting_knife", "ring_of_power", "ring_of_magic", "mana_charm", "bronze_mace"])),
}

quest_mapping = {
    "hunting_slimes": quest.Quest(
        "史莱姆狩猎",
        ev.quest_fight_against_slime_text,
        ev.shop_fight_against_slime_text,
        50, 50, items.equipment_data["zweihander"], event_mapping["fight_against_slime_combat"], 3
    ),
    "slime_king": quest.Quest(
        "史莱姆之王", 
        ev.quest_fight_against_slime_king_text, 
        ev.shop_fight_against_slime_king_text, 
        170, 230, items.equipment_data["long_bow"], event_mapping["fight_against_slime_king_combat"], 9
    ),
    "caesarus_bandit": quest.Quest(
        "凯撒鲁斯与他的强盗", 
        ev.quest_caesarus_bandit_text, 
        ev.shop_quest_caesarus_bandits, 
        150, 150, None, event_mapping["caesarus_bandit_combat"], 5
    ),
    "wolf_king": quest.Quest(
        "夜行狼王", 
        ev.quest_fight_against_wolf_king_text, 
        ev.shop_fight_against_wolf_king_text, 
        350, 700, items.equipment_data["wolf_king_proof"], event_mapping["wolf_king_combat"], 13
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
        "嘿, 冒险者, 请帮忙收集 5 份凝胶, 谢了!",
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
    name = data["name"]
    description = data["description"]
    danger_level = data["danger_level"]
    possible_enemies = data["possible_enemies"]

    shop_events = [event_mapping[name] for name in data["shop_events"]]
    heal_events = [event_mapping[name] for name in data["heal_events"]]
    special_events = [event_mapping[name] for name in data["special_events"]]
    quests = [quest_mapping[qname] for qname in data["quests"]]
    ascii_art = ascii_art_dict.get(data["ascii_art_key"], "")

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

    参数:
        ascii_art_dict: ASCII艺术字典，用于获取地区的视觉表示

    返回:
        Region: 表示雪之边境的地区对象
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

    参数:
        ascii_art_dict: ASCII艺术字典，用于获取地区的视觉表示

    返回:
        Region: 表示遗忘遗迹的地区对象
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
