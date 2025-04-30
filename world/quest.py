from rich.panel import Panel
from rich.console import Console
from rich.text import Text

console = Console()


class Quest():
    def __init__(self, name, description, proposal_text, xp_reward, gold_reward, item_reward, event, recommended_level) -> None:
        self.name = name
        self.description = description
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.item_reward = item_reward
        self.status = "Not Active"
        self.event = event
        self.proposal_text = proposal_text
        self.recommended_level = recommended_level

    def activate_quest(self, player):
        if self.status == "Not Active":
            self.status = "Active"
            player.active_quests.append(self)

    def complete_quest(self, player):
        if self.status == "Active":
            self.status = "Completed"
            player.active_quests.remove(self)
            player.completed_quests.append(self)
            self.give_rewards(player)

    def show_info(self):
        text = Text()
        text.append(f"{self.name}\n", style="bold yellow")
        text.append(f"推荐等级: {self.recommended_level}\n", style="cyan")
        text.append(self.description + "\n", style="white")
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
        """获取任务状态的中文描述"""
        status_dict = {
            "Not Active": "未接受",
            "Active": "进行中",
            "Completed": "已完成"
        }
        return status_dict.get(self.status, self.status)

    def give_rewards(self, player):
        print(f"任务 \"{self.name}\" 已完成。您获得了:")
        if self.xp_reward > 0:
            print(f"- {self.xp_reward}xp")
            player.add_exp(self.xp_reward)
        if self.gold_reward > 0:
            print(f"- {self.gold_reward}G")
            player.money += self.gold_reward
        if self.item_reward != None:
            print(f"- {self.item_reward.name}")
            self.item_reward.add_to_inventory_player(player.inventory)
