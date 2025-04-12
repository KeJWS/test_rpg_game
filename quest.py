
class Quest():
    '''
    定义任务，并处理任务的激活、完成和奖励发放。

    Attributes:
    name : str
        任务名称。
    description : str
        任务描述。
    proposalText : str
        任务发布时的文本信息。
    xpReward : int
        任务完成后获得的经验值奖励。
    goldReward : int
        任务完成后获得的金币奖励。
    itemReward : Item
        任务完成后获得的物品奖励。
    status : str
        当前任务的状态。
    event : Event
        任务触发的事件。
    recommendedLvl : int
        建议完成该任务的等级。
    '''
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
        '''
        激活任务，并将其添加到玩家的进行中任务列表。

        player : Player
            触发该任务的玩家。
        '''
        if self.status == "Not Active":
            self.status = "Active"
            self.event.add_event_to_event_list()
            player.active_quests.append(self)

    def complete_quest(self, player):
        '''
        完成任务，将其从进行中任务列表移除，并加入已完成任务列表。同时给予奖励。

        player : Player
            完成任务的玩家。
        '''
        if self.status == "Active":
            self.status = "Completed"
            player.active_quests.remove(self)
            player.completed_quests.append(self)
            self.give_rewards(player)

    def show_info(self):
        '''
        显示该任务的详细信息。
        '''
        print(f"\n - {self.name} - ")
        print(f"推荐级别: {self.recommended_level}")
        print(self.description)
        print("奖励:")
        if self.xp_reward > 0:
            print(f"XP: {self.xp_reward}")
        if self.gold_reward > 0:
            print(f"G: {self.gold_reward}")
        if self.item_reward != None:
            print(f"Item: {self.item_reward.name}")
        print("")

    def give_rewards(self, player):
        '''
        给予玩家任务奖励。

        Parameters:
        player : Player
            领取奖励的玩家。
        '''
        print(f"任务 \"{self.name}\" 已完成。您获得了 {self.xp_reward}xp 和 {self.gold_reward}G")
        if self.xp_reward > 0:
            player.add_exp(self.xp_reward)
        if self.gold_reward > 0:
            player.money += self.gold_reward
        if self.item_reward != None:
            self.item_reward.add_to_inventory(player.inventory())

    def propose_quest(self, player):
        '''
        向玩家发布任务，玩家可以选择接受或拒绝。

        Parameters:
        player : Player
            被提议任务的玩家。
        '''
        print(self.proposal_text)
        print(f"接受? [y/n] (推荐级别: {self.recommended_level})")
        option = input("> ").lower()
        while option not in ["y", "n"]:
            option = input("> ").lower()
        if option == "y":
            self.activate_quest(player)
