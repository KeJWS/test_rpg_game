"""
游戏世界地图模块，管理游戏中的地区、地理位置和事件生成系统。

该模块定义了游戏世界的地理结构和交互逻辑，包括地区的特性、
可能发生的事件、任务系统与地区的关联等。提供了玩家在世界中
移动、探索和与环境互动的核心功能。
"""

import json
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

import enemies
import events
import data.items_data as items_data
import world.quest as quest

console = Console()


@dataclass
class Region:
    """
    表示游戏世界中的一个地区。

    地区是游戏世界的基本地理单位，包含名称、描述、危险等级、可能遇到的敌人、
    商店事件、治疗事件、特殊事件、任务等信息。每个地区有自己的ASCII艺术表示和
    解锁状态。

    属性:
        name: 地区名称
        description: 地区描述
        danger_level: 危险等级，影响战斗难度
        possible_enemies: 可能遇到的敌人及其概率
        shop_events: 可能发生的商店事件列表
        heal_events: 可能发生的治疗事件列表
        special_events: 可能发生的特殊事件列表
        quests: 该地区可接取的任务列表
        ascii_art: 地区的ASCII艺术表示
        is_unlocked: 该地区是否已解锁
        quest_events: 与任务相关的事件列表
    """
    name: str
    description: str
    danger_level: int
    possible_enemies: Dict[str, Tuple[int, int]]
    shop_events: List[events.ShopEvent]
    heal_events: List[events.HealingEvent]
    special_events: List[events.Event]
    quests: List[quest.Quest]
    ascii_art: str
    is_unlocked: bool = True
    quest_events: List[events.Event] = None

    def available_quests(self, player):
        """
        返回该地区可接受的任务列表（未激活的）。

        筛选出该地区中未开始且未完成的任务，这些任务可供玩家接取。

        参数:
            player: 当前玩家对象

        返回:
            list: 可接受任务的列表
        """
        return [q for q in self.quests if q.status == "Not Active" and q not in player.completed_quests]

    def active_quests(self, player):
        """
        返回该地区已激活但未完成的任务。

        筛选出玩家已接取但尚未完成的该地区任务。

        参数:
            player: 当前玩家对象

        返回:
            list: 已激活未完成任务的列表
        """
        return [q for q in self.quests if q in player.active_quests]

    def completed_quests(self, player):
        """
        返回该地区已完成的任务。

        筛选出玩家在该地区已完成的任务。

        参数:
            player: 当前玩家对象

        返回:
            list: 已完成任务的列表
        """
        return [q for q in self.quests if q in player.completed_quests]

class World_map:
    """
    游戏世界地图类，管理所有地区和玩家在世界中的移动。

    该类负责初始化世界地图、管理地区之间的切换、生成随机事件、
    处理任务系统以及提供地区信息的显示功能。作为玩家与游戏世界
    交互的主要接口。
    """

    def __init__(self):
        """
        初始化世界地图对象。

        创建空的地区字典，设置当前地区为None，然后依次初始化
        所有地区、特殊事件和任务事件。
        """
        self.regions = {}
        self.current_region = None
        self._initialize_regions()
        self._initialize_special_events()
        self._initialize_quest_events()

    def _initialize_special_events(self):
        """
        初始化各地区的特殊事件。

        为各个地区创建并添加特殊事件，如BOSS战斗、环境危害等。
        这些事件通常具有较低的触发概率，但会对游戏进程产生较大影响。
        """
        shadow_wolf = enemies.enemy_data["shadow_wolf"].clone()
        forest_boss_combat = events.FixedCombatEvent(
            "影狼袭击", 
            [shadow_wolf]
        )

        self.regions["forest"].special_events.append(forest_boss_combat)

        poisonous_swamp_encounter = """
你不小心踩入一片冒着绿色气泡的沼泽地带。突然, 一股恶臭的气体从沼泽中涌出！
要屏住呼吸快速离开吗？(y/n)"""
        poisonous_swamp_success = "你成功憋住了呼吸, 迅速逃离了毒气区域！"
        poisonous_swamp_fail = "你吸入了一些毒气, 感到一阵头晕目眩, 生命值减少！"
        # poisonous_swamp_refuse = "你决定绕道而行, 避开了危险的沼泽地带。"

        swamp_poison_event = events.DamageEvent(
            "毒沼气", 
            poisonous_swamp_encounter,
            poisonous_swamp_success,
            poisonous_swamp_fail,
            30, 50
        )

        if "swamp" in self.regions:
            self.regions["swamp"].special_events.append(swamp_poison_event)

    def _initialize_regions(self):
        """
        初始化世界地图的所有地区。

        从JSON文件加载地区数据，使用地区工厂创建Region对象，
        并设置初始当前地区为城镇（town）。
        """
        from world.region_factory import load_region_from_dict
        ascii_art_dict = items_data.load_ascii_art_library("data/ascii_art/ascii_art_map.txt")
        with open("data/json_data/world_map.json", "r", encoding="utf-8") as f:
            all_region_data = json.load(f)

        self.regions = {}

        for key, region_data in all_region_data.items():
            self.regions[key] = load_region_from_dict(region_data, ascii_art_dict)
        for region in self.regions.values():
            region.quest_events = []

        self.current_region = self.regions["town"]

    def _initialize_quest_events(self):
        """
        初始化所有区域的任务事件。

        遍历所有地区的任务，提取任务关联的事件，并将其添加到
        相应地区的quest_events列表中，以便后续随机触发。
        """
        for region in self.regions.values():
            region.quest_events = []
            for q in region.quests:
                if hasattr(q, "event") and isinstance(q.event, events.Event):
                    region.quest_events.append(q.event)

    def unclock_region(self, region_name):
        """
        解锁指定地区。

        将指定名称的地区标记为已解锁状态，使玩家可以访问该地区。

        参数:
            region_name: 要解锁的地区名称

        返回:
            bool: 解锁成功返回True，地区不存在返回False
        """
        if region_name in self.regions:
            self.regions[region_name].is_unlocked = True
            return True
        return False

    def change_region(self, region_name):
        """
        切换到指定的地区。

        将当前地区更改为指定名称的地区。

        参数:
            region_name: 要切换到的地区名称

        返回:
            bool: 切换成功返回True，地区不存在返回False
        """
        if region_name in self.regions:
            self.current_region = self.regions[region_name]
            return True
        return False

    def get_current_region_info(self):
        """
        获取并显示当前地区的信息。

        使用rich格式化输出当前地区的ASCII艺术、危险等级和描述信息。
        如果当前地区未设置，则显示未知地区信息。
        """
        if self.current_region:
            text = Text()
            text.append(self.current_region.ascii_art + "\n\n", style="bold white")
            text.append(f"危险等级: {'★ ' * self.current_region.danger_level}\n", style="bold red")
            text.append(self.current_region.description, style="italic")
            console.print(Panel.fit(text, title=f"当前位置: ", subtitle=self.current_region.name, border_style="bold green"))
        else:
            console.print("[red]未知地区[/red]")

    def list_available_regions(self):
        """
        列出所有可前往的地区。

        使用rich表格格式显示所有地区的编号、名称和危险等级，
        帮助玩家选择要前往的地区。
        """
        table = Table(title="可探索地区", header_style="bold green")
        table.add_column("编号", justify="center")
        table.add_column("地区名称")
        table.add_column("危险等级", style="bold red")
        for i, region in enumerate(self.regions.values()):
            table.add_row(str(i+1), region.name, "★ " * region.danger_level)
        console.print(table)

    def show_region_quests(self, player):
        """
        显示当前地区的任务情况。

        分类显示当前地区的可接受任务、正在进行的任务和已完成的任务。
        每个任务显示其名称和推荐等级。

        参数:
            player: 当前玩家对象

        返回:
            list: 可接受任务的列表，用于后续任务接取操作
        """
        if not self.current_region:
            console.print("[red]未知地区, 无法查看任务[/red]")
            return

        available_quests = self.current_region.available_quests(player)
        active_quests = self.current_region.active_quests(player)
        completed_quests = self.current_region.completed_quests(player)

        console.print(Panel.fit(f"[bold white]{self.current_region.name} 的任务一览[/bold white]", border_style="bright_green"))

        def show_quests(title, quests, style):
            if quests:
                console.print(f"[{style}]{title}[/]:")
                for i, q in enumerate(quests, 1):
                    console.print(f"  [white]{i}. {q.name}[/] (推荐等级: {q.recommended_level})")
            else:
                console.print(f"[dim]{title}：无[/dim]")

        show_quests("可接受任务", available_quests, "green")
        show_quests("正在进行", active_quests, "blue")
        show_quests("已完成任务", completed_quests, "magenta")
        return available_quests

    def accept_quest(self, player, quest_index, available_quests):
        """
        接受地区任务。

        根据提供的任务索引，让玩家接受指定的任务。
        显示任务描述并询问玩家是否接受，如接受则激活任务。

        参数:
            player: 当前玩家对象
            quest_index: 要接受的任务在可用任务列表中的索引
            available_quests: 可用任务列表
        """
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
        """
        根据当前地区生成随机事件。

        基于提供的概率参数，在当前地区生成战斗、商店或治疗事件。
        优先考虑活跃任务相关的事件，其次考虑普通随机事件，
        最后有小概率触发特殊事件。

        参数:
            player: 当前玩家对象
            combot_chance: 战斗事件发生的概率（0-100）
            shop_chance: 商店事件发生的概率（0-100）
            heal_chance: 治疗事件发生的概率（0-100）
        """
        if not self.current_region:
            return

        active_quest_events = [
            q.event for q in player.active_quests 
            if hasattr(q, 'event') and q.event in self.current_region.quest_events
        ]

        if active_quest_events:
            if random.randint(1, 100) <= 70:
                quest_event = random.choice(active_quest_events)
                print(f"\n一个任务相关事件发生了: {quest_event.name}")
                escaped = quest_event.effect(player)
                if quest_event.is_unique and not escaped and player.alive:
                    self.current_region.quest_events.remove(quest_event)
                    for q in player.active_quests:
                        if hasattr(q, 'event') and q.event == quest_event:
                            q.complete_quest(player)
                elif quest_event.is_unique and escaped:
                    console.print("你逃离了战斗, 还有机会再尝试完成任务", style="yellow")
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
            combat_event = events.RandomCombatEvent(f"{self.current_region.name}的随机战斗")
            enemies.possible_enemies = self.current_region.possible_enemies
            combat_event.effect(player)
            return
        elif event_type == "shop":
            shop_event = random.choice(self.current_region.shop_events)
            shop_event.effect(player)
        elif event_type == "heal":
            heal_event = random.choice(self.current_region.heal_events)
            heal_event.effect(player)

        if (self.current_region.special_events and 
            random.randint(1, 100) <= 7):
            special_event = random.choice(self.current_region.special_events)
            print(f"\n一个特殊事件发生了: {special_event.name}")
            escaped = special_event.effect(player)
            if special_event.is_unique and not escaped and player.alive:
                self.current_region.special_events.remove(special_event)
            elif special_event.is_unique and escaped:
                console.print("你逃离了战斗...", style="yellow")
                pass

world_map = World_map()
