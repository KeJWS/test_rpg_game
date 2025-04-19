import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from copy import deepcopy

import enemies, events, items, quest
import test.fx as fx
import data.event_text as event_text

@dataclass
class Region:
    name: str
    description: str
    danger_level: int
    possible_enemies: Dict[str, Tuple[int, int]]
    shop_events: List[events.Shop_event]
    heal_events: List[events.Healing_event]
    special_events: List[events.Event]
    quests: List[quest.Quest]
    ascii_art: str
    is_unlocked: bool = True

    def available_quests(self, player):
        """返回该地区可接受的任务列表（未激活的）"""
        return [q for q in self.quests if q.status == "Not Active" and q not in player.completed_quests]

    def active_quests(self, player):
        """返回该地区已激活但未完成的任务"""
        return [q for q in self.quests if q in player.active_quests]

    def completed_quests(self, player):
        """返回该地区已完成的任务"""
        return [q for q in self.quests if q in player.completed_quests]

class World_map:
    def __init__(self):
        self.regions = {}
        self.current_region = None
        self._initialize_regions()
        self._initialize_special_events()

    def _initialize_special_events(self):
        """初始化各地区的特殊事件"""
        shadow_wolf = enemies.enemy_data["shadow_wolf"].clone()
        forest_boss_combat = events.Fixed_combat_event(
            "影狼袭击", 
            [shadow_wolf]
        )

        self.regions["forest"].special_events.append(forest_boss_combat)

    def _initialize_regions(self):
        ascii_art_dict = items.load_ascii_art_library("data/ascii_art_map.txt")

        forest = self._create_forest(ascii_art_dict)
        town = self._create_town(ascii_art_dict)
        mountain = self._create_mountain(ascii_art_dict)
        # redflame_canyon = self._create_redflame_canyon(ascii_art_dict)
        # snowlands = self._create_snowlands(ascii_art_dict)
        # forgotten_ruins = self._create_forgotten_ruins(ascii_art_dict)

        self.regions = {
            "town": town,
            "forest": forest,
            "mountain": mountain,
            # "redflame canyon": redflame_canyon,
            # "snowlands": snowlands,
            # "forgotten ruins": forgotten_ruins,
        }

        self.current_region = self.regions["town"]

    def _create_forest(self, ascii_art_dict):
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
                                             event_text.quest_fight_against_slime_text,
                                             event_text.shop_fight_against_slime_text,
                                             50, 50, items.equipment_data["zweihander"], fight_against_slime_combat, 3)

        fight_against_slime_king_combat = events.Fixed_combat_event("史莱姆之王", enemies.enemy_list_fight_against_slime_king)
        fight_against_slime_king_quest = quest.Quest("史莱姆之王", 
                                             event_text.quest_fight_against_slime_king_text, 
                                             event_text.shop_fight_against_slime_king_text, 
                                             170, 230, items.equipment_data["long_bow"], fight_against_slime_king_combat, 9)
        forest = Region(
            name="雾林",
            description="一片神秘的森林, 低级怪物在这里游荡。适合初学者冒险, \n不过要小心这里的森林守卫者",
            danger_level=1,
            possible_enemies=forest_enemies,
            shop_events=[events.shop_itz_magic],
            heal_events=[events.heal_medussa_statue],
            special_events=[],
            quests=[fight_against_slime_quest, fight_against_slime_king_quest],
            ascii_art=ascii_art_dict.get("雾林", "")
        )
        return forest

    def _create_town(self, ascii_art_dict):
        town = Region(
            name="安全镇",
            description="一个和平的小镇, 这里没有敌人, 但有许多商店和休息的地方",
            danger_level=0,
            possible_enemies={},
            shop_events=[events.shop_jack_weapon, events.shop_anna_armor],
            heal_events=[events.inn_event],
            special_events=[],
            quests=[],
            ascii_art=ascii_art_dict.get("安全镇", "")
        )
        return town

    def _create_mountain(self, ascii_art_dict):
        caesarus_bandit_combat = events.Fixed_combat_event("凯撒鲁斯与他的强盗", enemies.enemy_list_caesarus_bandit)
        caesarus_bandit_quest = quest.Quest("凯撒鲁斯与他的强盗", 
                                          event_text.quest_caesarus_bandit_text, 
                                          event_text.shop_quest_caesarus_bandits, 
                                          150, 150, None, caesarus_bandit_combat, 5)

        wolf_king_combat = events.Fixed_combat_event("夜行狼王", enemies.enemy_list_fight_against_wolf_king)
        wolf_king_quest = quest.Quest("夜行狼王", 
                                          event_text.quest_fight_against_wolf_king_text, 
                                          event_text.shop_fight_against_wolf_king_text, 
                                          350, 700, items.equipment_data["wolf_king_proof"], wolf_king_combat, 13)
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
            shop_events=[events.shop_rik_armor],
            heal_events=[events.heal_medussa_statue],
            special_events=[],
            quests=[caesarus_bandit_quest, wolf_king_quest],
            ascii_art=ascii_art_dict.get("龙脊山", "")
        )
        return mountain

    def _create_redflame_canyon(self, ascii_art_dict):
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

    def _create_snowlands(self, ascii_art_dict):
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

    def _create_forgotten_ruins(self, ascii_art_dict):
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

    def unclock_region(self, region_name):
        """解锁指定地区"""
        if region_name in self.regions:
            self.regions[region_name].is_unlocked = True
            return True
        return False

    def change_region(self, region_name):
        """切换到指定的地区"""
        if region_name in self.regions:
            self.current_region = self.regions[region_name]
            return True
        return False

    def get_current_region_info(self):
        """获取当前地区的信息"""
        if self.current_region:
            return (
                f"\n{fx.GREEN}{self.current_region.ascii_art}{fx.END}\n"
                f"\n当前位置: {self.current_region.name}\n"
                f"危险等级: {'★ ' * self.current_region.danger_level}\n"
                f"{self.current_region.description}"
            )
        return "未知地区"

    def list_available_regions(self):
        """列出所有可前往的地区"""
        return "\n".join([
            f"{i+1}. {region.name} 危险等级: {'★ ' * region.danger_level}" 
            for i, region in enumerate(self.regions.values())
        ])

    def show_region_quests(self, player):
        """显示当前地区的任务情况"""
        if not self.current_region:
            print("未知地区, 无法查看任务")
            return

        available_quests = self.current_region.available_quests(player)
        active_quests = self.current_region.active_quests(player)
        completed_quests = self.current_region.completed_quests(player)

        print(f"\n=== {self.current_region.name} 的任务 ===")

        if available_quests:
            print("可接受的任务:")
            for i, q in enumerate(available_quests):
                print(f"{i+1}. {q.name} (推荐等级: {q.recommended_level})")
        else:
            print("\n当前没有可接受的任务")

        if active_quests:
            print("\n正在进行的任务:")
            for q in active_quests:
                print(f"- {q.name} (进行中)")

        if completed_quests:
            print("\n已完成的任务:")
            for q in completed_quests:
                print(f"- {q.name} (已完成)")

        return available_quests

    def accept_quest(self, player, quest_index, available_quests):
        """接受地区任务"""
        if 0 <= quest_index < len(available_quests):
            quest_to_accept = available_quests[quest_index]
            print("\n" + quest_to_accept.proposal_text)
            print(f"接受? [y/n] (推荐级别: {quest_to_accept.recommended_level})")
            option = input("> ").lower()
            while option not in ["y", "n"]:
                option = input("> ").lower()
            if option == "y":
                quest_to_accept.activate_quest(player)
                print(f"已接受任务: {quest_to_accept.name}")
            else:
                print("已拒绝任务")
        else:
            print("无效的任务选择")

    def generate_random_event(self, player, combot_chance, shop_chance, heal_chance):
        """根据当前地区生成随机事件"""
        if not self.current_region:
            return

        if self.current_region.danger_level == 0:
            combot_chance = 0

        event_types = []
        weights = []

        if self.current_region.possible_enemies and combot_chance > 0:
            event_types.append("combat")
            weights.append(combot_chance)

        if self.current_region.shop_events and shop_chance > 0:
            event_types.append("shop")
            weights.append(shop_chance)

        if self.current_region.heal_events and heal_chance > 0:
            event_types.append("heal")
            weights.append(heal_chance)

        if not event_types:
            print("这个地区目前很平静, 没有发生任何事件")
            return

        event_type = random.choices(event_types, weights=weights, k=1)[0]

        if event_type == "combat":
            combat_event = events.Random_combat_event(f"{self.current_region.name}的随机战斗")
            enemies.possible_enemies = self.current_region.possible_enemies
            combat_event.effect(player)

        elif event_type == "shop":
            shop_event = random.choice(self.current_region.shop_events)
            shop_event.effect(player)

        elif event_type == "heal":
            heal_event = random.choice(self.current_region.heal_events)
            heal_event.effect(player)

        if (self.current_region.special_events and 
            random.randint(1, 100) <= 10):
            special_event = random.choice(self.current_region.special_events)
            print(f"\n一个特殊事件发生了: {special_event.name}")
            escaped = special_event.effect(player)
            if special_event.is_unique and not escaped and player.alive:
                self.current_region.special_events.remove(special_event)
                for quest in player.active_quests:
                    if hasattr(quest, 'event') and quest.event == special_event:
                        quest.complete_quest(player)
            elif special_event.is_unique and escaped:
                print(fx.yellow("你逃离了战斗, 不过没关系还可以再次尝试"))
                pass

world_map = World_map()
