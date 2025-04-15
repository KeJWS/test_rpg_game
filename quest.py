
class Quest():
    def __init__(self, name, description, proposal_text, xp_reward, gold_reward, item_reward, event, recommended_level) -> None:
        self.name = name
        self.description = description
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.item_reward = item_reward
        # TODO: 修改任务状态的处理方式
        self.status = "Not Active"
        self.event = event
        self.proposal_text = proposal_text
        self.recommended_level = recommended_level

    def activate_quest(self, player):
        if self.status == "Not Active":
            self.status = "Active"
            self.event.add_event_to_event_list()
            player.active_quests.append(self)

    def complete_quest(self, player):
        if self.status == "Active":
            self.status = "Completed"
            player.active_quests.remove(self)
            player.completed_quests.append(self)
            self.give_rewards(player)

    def show_info(self):
        print(f"\n - {self.name} - ")
        print(f"推荐级别: {self.recommended_level}")
        print(self.description)
        print("奖励:")
        if self.xp_reward > 0:
            print(f"XP: {self.xp_reward}")
        if self.gold_reward > 0:
            print(f"G: {self.gold_reward}")
        if self.item_reward != None:
            print(f"物品: {self.item_reward.name}")
        print("")
        from map import world_map
        for region_name, region in world_map.regions.items():
            if self in region.quests:
                print(f"\n所在地区: {region.name}")
                break

        print("")

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
