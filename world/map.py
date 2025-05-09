import json
import random
from dataclasses import dataclass
from copy import deepcopy
from typing import List, Dict, Tuple, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

import enemies, events, items
import world.quest as quest

console = Console()


@dataclass
class Region:
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
        self._initialize_quest_events()

    def _initialize_special_events(self):
        """初始化各地区的特殊事件"""
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
        from world.region_factory import load_region_from_dict
        ascii_art_dict = items.load_ascii_art_library("data/ascii_art/ascii_art_map.txt")
        with open("data/json_data/world_map.json", "r", encoding="utf-8") as f:
            all_region_data = json.load(f)

        self.regions = {}

        for key, region_data in all_region_data.items():
            self.regions[key] = load_region_from_dict(region_data, ascii_art_dict)
        for region in self.regions.values():
            region.quest_events = []

        self.current_region = self.regions["town"]

    def _initialize_quest_events(self):
        """初始化所有区域的任务事件"""
        for region in self.regions.values():
            region.quest_events = []
            for q in region.quests:
                if hasattr(q, "event") and isinstance(q.event, events.Event):
                    region.quest_events.append(q.event)

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
            text = Text()
            text.append(self.current_region.ascii_art + "\n\n", style="bold white")
            text.append(f"危险等级: {'★ ' * self.current_region.danger_level}\n", style="bold red")
            text.append(self.current_region.description, style="italic")
            console.print(Panel.fit(text, title=f"当前位置: ", subtitle=self.current_region.name, border_style="bold green"))
        else:
            console.print("[red]未知地区[/red]")

    def list_available_regions(self):
        """列出所有可前往的地区"""
        table = Table(title="可探索地区", header_style="bold green")
        table.add_column("编号", justify="center")
        table.add_column("地区名称")
        table.add_column("危险等级", style="bold red")
        for i, region in enumerate(self.regions.values()):
            table.add_row(str(i+1), region.name, "★ " * region.danger_level)
        console.print(table)

    def show_region_quests(self, player):
        """显示当前地区的任务情况"""
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
