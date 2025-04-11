
class Quest():
    def __init__(self, name, text, xp_reward, gold_reward, item_reward, event, proposal_text) -> None:
        self.name = name
        self.text = text
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.item_reward = item_reward
        self.status = "Not Active"
        self.event = event
        self.proposal_text = proposal_text

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
        print("----------------------------------")
        print(f" - {self.name} - ")
        print(self.text)
        print("Rewards:")
        if self.xp_reward > 0:
            print(f"XP: {self.xp_reward}")
        if self.gold_reward > 0:
            print(f"G: {self.gold_reward}")
        if self.item_reward != None:
            print(f"Item: {self.item_reward.name}")

    def give_rewards(self, player):
        print(f"\"{self.name}\" 任务已完成。您获得了 {self.xp_reward}xp 和 {self.gold_reward}G")
        if self.xp_reward > 0:
            player.add_exp(self.xp_reward)
        if self.gold_reward > 0:
            player.money += self.gold_reward
        if self.item_reward != None:
            self.item_reward.add_to_inventory(player.inventory())

    def propose_quest(self, player):
        print(self.proposal_text)
        print("接受? [y/n]")
        option = input("> ").lower()
        while option not in ["y", "n"]:
            option = input("> ").lower()
        if option == "y":
            self.activate_quest(player)
