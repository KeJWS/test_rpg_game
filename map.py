import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import enemies, events, items
from copy import deepcopy

import test.fx as fx

@dataclass
class Region:
    name: str
    description: str
    danger_level: int # 影响敌人等级和数量
    possible_enemies: Dict[str, Tuple[int, int]] # 每个地区的敌人池 {enemy_name: (min_level, max_level)}
    shop_events: List[events.Shop_event]
    heal_events: List[events.Healing_event]
    special_events: List[events.Event]
    ascii_art: str
    is_unclocked: bool = True

class World_map:
    def __init__(self):
        self.regions = {}
        self.current_region = None
        self._initialize_regions()
        self._initialize_special_events()

    def _initialize_special_events(self):
        """初始化各地区的特殊事件"""
        poisonous_swamp_encounter = """
你不小心踩入一片冒着绿色气泡的沼泽地带。突然, 一股恶臭的气体从沼泽中涌出!
要屏住呼吸快速离开吗?(y/n)
"""
        poisonous_swamp_success = "你成功憋住了呼吸, 迅速逃离了毒气区域!"
        poisonous_swamp_fail = "你吸入了一些毒气, 感到一阵头晕目眩, 生命值减少!"
        poisonous_swamp_refuse = "你决定绕道而行, 避开了危险的沼泽地带"
        swamp_poison_event = events.Healing_event(
            "毒沼气",
            poisonous_swamp_encounter,
            poisonous_swamp_success,
            poisonous_swamp_fail,
            poisonous_swamp_refuse,
            40, False, -30
        )

        if "swamp" in self.regions:
            self.regions["swamp"].special_events.append(swamp_poison_event)

    def _initialize_regions(self):
        ascii_art_dict = items.load_ascii_art_library("data/ascii_art_map.txt")
        forest_enemies = {
            "slime": (1, 3),
            "imp": (1, 4),
            "giant_slime": (3, 100)
        }

        forest = Region(
            name="雾林",
            description="一片神秘的森林, 低级怪物在这里游荡。适合初学者冒险",
            danger_level=1,
            possible_enemies=forest_enemies,
            shop_events=[events.shop_itz_magic],
            heal_events=[events.heal_medussa_statue],
            special_events=[],
            ascii_art=ascii_art_dict.get("雾林", "")
        )

        mountain_ascii = """
        /\\  /\\  /\\  /\\  /\\
        |   Mountain   |
        /\\  /\\  /\\  /\\  /\\
           /\\_/\\_/\\_/\\
          /         \\
         /           \\
        """

        town = Region(
            name="安全镇",
            description="一个和平的小镇, 这里没有敌人, 但有许多商店和休息的地方",
            danger_level=0,
            possible_enemies={},
            shop_events=[events.shop_rik_armor],
            heal_events=[events.inn_event],
            special_events=[],
            ascii_art=ascii_art_dict.get("安全镇", "")
        )

        swamp_ascii = """
        ~~~~~~~~~~~~~~~~~~~
        |      Swamp     |
        ~~~~~~~~~~~~~~~~~~~
        ~   ~   ~   ~   ~
         ~ ~ ~ ~ ~ ~ ~ ~ ~
        ~   ~   ~   ~   ~
        """

        self.regions = {
            "town": town,
            "forest": forest,
        }

        self.current_region = self.regions["town"]

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
                f"{fx.GREEN}\n{self.current_region.ascii_art}{fx.END}\n"
                f"当前位置: {self.current_region.name}\n"
                f"危险等级: {'★' * self.current_region.danger_level}\n"
                f"{self.current_region.description}"
            )
        return "未知地区"

    def list_avaliable_regions(self):
        """列出所有可前往的地区"""
        return "\n".join([
            f"{i+1}. {region.name} (危险等级: {'★' * region.danger_level})" 
            for i, region in enumerate(self.regions.values())
        ])

    def generate_random_event(self, player, combot_chance, shop_chance, heal_chance):
        """根据当前地区生成随机事件"""
        if not self.current_region:
            return

        if self.current_region.danger_level == 0:
            combot_chance = 0
            total = shop_chance + heal_chance
            shop_chance = int(shop_chance / total * 100)
            heal_chance = 100 - shop_chance

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
            old_enemies = enemies.possible_enemies
            enemies.possible_enemies = self.current_region.possible_enemies
            combat_event.effect(player)
            enemies.possible_enemies = old_enemies

        elif event_type == "shop":
            shop_event = random.choice(self.current_region.shop_events)
            shop_event.effect(player)

        elif event_type == "heal":
            heal_event = random.choice(self.current_region.heal_events)
            heal_event.effect(player)

        if (self.current_region.special_events and 
            random.randint(1, 100) <= 10):
            special_event = random.choice(self.current_region.special_events)
            print("\n一个特殊事件发生了!")
            special_event.effect(player)
            if special_event.is_unique:
                self.current_region.special_events.remove(special_event)
                for quest in player.active_quests:
                    if hasattr(quest, 'event') and quest.event == special_event:
                        quest.complete_quest(player)

world_map = World_map()
