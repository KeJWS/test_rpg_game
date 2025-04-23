import events, enemies, items
from world import quest
import data.event_text as ev
from world.map import Region

def create_forest(ascii_art_dict):
    forest_enemies = {
        "slime": (1, 3),
        "imp": (1, 5),
        "forest_spider": (2, 7),
        "poison_frog": (2, 9),
        "giant_slime": (4, 23),
        "shadow_wolf": (8, 16),
    }
    fight_against_slime_combat = events.Fixed_combat_event("史莱姆狩猎", enemies.enemy_list_fight_against_slime)
    fight_against_slime_quest = quest.Quest("史莱姆狩猎",
                                         ev.quest_fight_against_slime_text,
                                         ev.shop_fight_against_slime_text,
                                         50, 50, items.equipment_data["zweihander"], fight_against_slime_combat, 3)
    fight_against_slime_king_combat = events.Fixed_combat_event("史莱姆之王", enemies.enemy_list_fight_against_slime_king)
    fight_against_slime_king_quest = quest.Quest("史莱姆之王", 
                                         ev.quest_fight_against_slime_king_text, 
                                         ev.shop_fight_against_slime_king_text, 
                                         170, 230, items.equipment_data["long_bow"], fight_against_slime_king_combat, 9)
    forest = Region(
        name="雾林",
        description="一片神秘的森林, 低级怪物在这里游荡。\n适合初学者冒险, 不过要小心这里的森林守卫者。",
        danger_level=1,
        possible_enemies=forest_enemies,
        shop_events=[],
        heal_events=[events.heal_medussa_statue],
        special_events=[],
        quests=[fight_against_slime_quest, fight_against_slime_king_quest],
        ascii_art=ascii_art_dict.get("雾林", "")
    )
    return forest

def create_town(ascii_art_dict):
    town = Region(
        name="安全镇",
        description="一个和平的小镇, 这里没有敌人, \n但有许多商店和休息的地方。",
        danger_level=0,
        possible_enemies={},
        shop_events=[events.shop_jack_weapon, events.shop_anna_armor],
        heal_events=[events.inn_event],
        special_events=[],
        quests=[],
        ascii_art=ascii_art_dict.get("安全镇", "")
    )
    return town

def create_mountain(ascii_art_dict):
        caesarus_bandit_combat = events.Fixed_combat_event("凯撒鲁斯与他的强盗", enemies.enemy_list_caesarus_bandit)
        caesarus_bandit_quest = quest.Quest("凯撒鲁斯与他的强盗", 
                                          ev.quest_caesarus_bandit_text, 
                                          ev.shop_quest_caesarus_bandits, 
                                          150, 150, None, caesarus_bandit_combat, 5)

        mountain_enemies = {
            "golem": (1, 7),
            "skeleton": (3, 10),
            "bandit": (4, 12),
            "wild_boar": (6, 15),
            "wolf": (8, 22),
        }
        mountain = Region(
            name="龙脊山",
            description="危险的山脉地带, 强盗和山地怪物出没。",
            danger_level=2,
            possible_enemies=mountain_enemies,
            shop_events=[events.shop_rik_armor, events.shop_lok_armor],
            heal_events=[events.heal_medussa_statue],
            special_events=[],
            quests=[caesarus_bandit_quest],
            ascii_art=ascii_art_dict.get("龙脊山", "")
        )
        return mountain

def create_swamp_herbalist(ascii_art_dict):
        wolf_king_combat = events.Fixed_combat_event("夜行狼王", enemies.enemy_list_fight_against_wolf_king)
        wolf_king_quest = quest.Quest("夜行狼王", 
                                          ev.quest_fight_against_wolf_king_text, 
                                          ev.shop_fight_against_wolf_king_text, 
                                          350, 700, items.equipment_data["wolf_king_proof"], wolf_king_combat, 13)

        swamp_enemies = {
            "forest_spider": (1, 7),
            "poison_frog": (1, 9),
            "giant_slime": (3, 15),
        }
        swamp = Region(
            name="迷雾沼泽",
            description="一片危险的沼泽地带, 充满毒气和致命的生物。\n地面松软, 行动困难。",
            danger_level=3,
            possible_enemies=swamp_enemies,
            shop_events=[events.shop_itz_magic],
            heal_events=[events.heal_medussa_statue],
            special_events=[],
            quests=[wolf_king_quest],
            ascii_art=ascii_art_dict.get("迷雾沼泽", "")
        )
        return swamp

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
