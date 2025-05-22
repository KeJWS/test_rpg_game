"""
任务系统模块，定义游戏中的任务结构和管理逻辑。

该模块实现了游戏中的任务系统，包括任务的创建、激活、完成和奖励发放。
支持多种任务类型，如收集物品、完成特定事件等，并提供了任务状态管理和
信息显示功能。
"""

from rich.panel import Panel
from rich.console import Console
from rich.text import Text

console = Console()


class Quest():
    """
    任务类，表示游戏中可接取和完成的任务。

    任务是游戏中重要的进度和奖励系统，玩家可以接取任务、完成任务目标
    并获得相应奖励。任务可以包含经验、金币和物品奖励，可能需要完成特定
    事件或收集指定物品。
    """

    def __init__(self, name, description, proposal_text, xp_reward, gold_reward, item_reward, event, recommended_level, required_items=None):
        """
        初始化一个任务对象。

        创建一个新的任务，设置其基本属性、奖励、关联事件和完成条件。
        初始状态为"未激活"(Not Active)。

        参数:
            name: 任务名称
            description: 任务描述
            proposal_text: 任务提示文本，显示给玩家决定是否接受任务
            xp_reward: 完成任务获得的经验值
            gold_reward: 完成任务获得的金币
            item_reward: 完成任务获得的物品
            event: 与任务关联的事件对象
            recommended_level: 推荐的玩家等级
            required_items: 需要收集的物品及数量，格式为字典 {"物品名": 数量}
        """
        self.name = name
        self.description = description
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.item_reward = item_reward
        self.status = "Not Active"
        self.event = event
        self.proposal_text = proposal_text
        self.recommended_level = recommended_level
        self.required_items = required_items or {}  # e.g., {"狼皮": 5}

    def activate_quest(self, player):
        """
        激活任务。

        将任务状态从"未激活"更改为"激活"，并将其添加到玩家的
        活跃任务列表中。只有未激活的任务可以被激活。

        参数:
            player: 要激活任务的玩家对象
        """
        if self.status == "Not Active":
            self.status = "Active"
            player.active_quests.append(self)

    def complete_quest(self, player):
        """
        完成任务。

        将任务状态从"激活"更改为"已完成"，从玩家的活跃任务列表中移除，
        添加到已完成任务列表，并发放任务奖励。只有激活状态的任务可以被完成。

        参数:
            player: 完成任务的玩家对象
        """
        if self.status == "Active":
            self.status = "Completed"
            player.active_quests.remove(self)
            player.completed_quests.append(self)
            self.give_rewards(player)

    def show_info(self, player):
        """
        显示任务详细信息。

        以格式化的方式显示任务的名称、描述、推荐等级、收集目标、
        奖励和所在地区等信息。如果任务需要收集物品，会显示当前
        收集进度。

        参数:
            player: 当前玩家对象，用于检查物品收集进度
        """
        text = Text()
        text.append(f"{self.name}\n", style="bold yellow")
        text.append(f"推荐等级: {self.recommended_level}\n", style="cyan")
        text.append(self.description + "\n", style="white")
        if self.required_items:
            text.append("收集目标:\n")
            for name, count in self.required_items.items():
                current = player.inventory.count_item_by_name(name)
                text.append(f"  - {name}: {current}/{count}\n")

        text.append("奖励:\n", style="green")
        if self.xp_reward:
            text.append(f"  - 经验: {self.xp_reward}\n", style="green")
        if self.gold_reward:
            text.append(f"  - 金币: {self.gold_reward}\n", style="green")
        if self.item_reward:
            text.append(f"  - 物品: {self.item_reward.name}\n", style="green")

        from world.map import world_map
        for region_name, region in world_map.regions.items():
            if self in region.quests:
                text.append(f"\n所在地区: {region.name}")
                console.print(Panel.fit(text, title="任务详情", border_style="bright_blue"))
                break

    def get_status_text(self):
        """
        获取任务状态的中文描述。

        将内部使用的英文状态转换为适合显示的中文描述。

        返回:
            str: 任务状态的中文描述
        """
        status_dict = {
            "Not Active": "未接受",
            "Active": "进行中",
            "Completed": "已完成"
        }
        return status_dict.get(self.status, self.status)

    def give_rewards(self, player):
        """
        发放任务奖励给玩家。

        根据任务设定的奖励，为玩家添加经验值、金币和物品。
        打印完成任务的提示信息和获得的物品奖励。

        参数:
            player: 要发放奖励的玩家对象
        """
        print(f"任务 \"{self.name}\" 已完成")
        if self.xp_reward > 0:
            player.add_exp(self.xp_reward)
        if self.gold_reward > 0:
            player.add_money(self.gold_reward)
        if self.item_reward != None:
            print(f"- {self.item_reward.name}")
            self.item_reward.add_to_inventory_player(player.inventory)

    def check_item_collection(self, player):
        """
        检查玩家背包是否已满足任务收集条件。

        遍历任务所需的物品列表，检查玩家背包中是否有足够数量的每种物品。

        参数:
            player: 要检查的玩家对象

        返回:
            bool: 如果所有物品都收集足够，返回True；否则返回False
        """
        if self.required_items:
            for item_name, required_count in self.required_items.items():
                inventory_count = player.inventory.count_item_by_name(item_name)
                if inventory_count < required_count:
                    return False
            return True
        return False

    def try_complete_collection(self, player):
        """
        尝试完成收集类任务。

        检查是否满足收集条件，如果满足则完成任务并从玩家背包中
        移除所需物品。适用于物品收集类型的任务。
        """
        if self.status == "Active" and self.check_item_collection(player):
            print(f"已收集完所需物品，任务『{self.name}』完成！")
            self.complete_quest(player)
            for item_name, required_count in self.required_items.items():
                removed = player.inventory.remove_items_by_name(item_name, required_count)
                if removed:
                    print(f"\n- 交出物品: {item_name} x{required_count}")
