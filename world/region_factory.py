import random
import events, enemies, items
from world import quest
import data.event_text as ev
from world.map import Region

event_mapping = {
    "shop_jack_weapon": events.shop_jack_weapon,
    "shop_anna_armor": events.shop_anna_armor,
    "inn_event": events.inn_event,
    "heal_medussa_statue": events.heal_medussa_statue,
    "fight_against_slime_combat": events.Fixed_combat_event("史莱姆狩猎", enemies.enemy_list_fight_against_slime),
    "fight_against_slime_king_combat": events.Fixed_combat_event("史莱姆之王", enemies.enemy_list_fight_against_slime_king),
    "shop_rik_armor": events.shop_rik_armor,
    "shop_lok_armor": events.shop_lok_armor,
    "caesarus_bandit_combat": events.Fixed_combat_event("凯撒鲁斯与他的强盗", enemies.enemy_list_caesarus_bandit),
    "shop_itz_magic": events.shop_itz_magic,
    "wolf_king_combat": events.Fixed_combat_event("夜行狼王", enemies.enemy_list_fight_against_wolf_king),

    "find_coins": events.SimpleEvent("发现零钱", events.find_coins),
    "admire_scenery": events.SimpleEvent("欣赏美景", events.admire_scenery),
    "friendly_villager": events.SimpleEvent("村民物资", events.friendly_villager),
    "find_herb": events.SimpleEvent("找到草药", events.find_herb),
    "rest_spot": events.SimpleEvent("短暂休息", events.rest_spot),

    "mysterious_businessman": events.Shop_event("神秘商人", False, ev.mysterious_businessman_encounter, ev.mysterious_businessman_enter, \
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
