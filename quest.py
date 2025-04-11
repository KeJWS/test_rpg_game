
class Quest():
    def __init__(self, name, text, xp_reward, gold_reward, item_reward) -> None:
        self.name = name
        self.text = text
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.item_reward = item_reward
        self.status = "Not Active"

    def activate_quest(self, player):
        if self.status == "Not Active":
            self.status = "Active"
            player.active_quests.append(self)

    def complete_quest(self, player):
        if self.status == "Active":
            self.status = "Completed"
            player.completed_quests.append(self)

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
