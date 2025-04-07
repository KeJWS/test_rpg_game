import combat

"""
管理玩家的库存和物品。可以修改为具有一定容量。
"""
class Inventory():
    def __init__(self) -> None:
        self.items = []

    def show_inventory(self): # 显示库存中的所有物品
        if not self.items:
            print("背包是空的。")
        print(f"总价值: {self.total_worth}")
        for index, item in enumerate(self.items, start=1):
            print(f"{index} - {item.show_info()}")

    def drop_item(self):
        print("\n丢掉什么? ['0' 退出]") # 从库存中丢弃一个物品
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
        elif i <= len(self.items):
            item = self.items[i-1]
            item.drop()
            if item.amount <= 0:
                self.items.pop(i-1)
            print('现在你的背包如下：')
            self.show_inventory()

    def sell_item(self):
        print("\n出售什么? ['0' 退出]") # 出售库存中的特定物品
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
            return 0
        elif i <= len(self.items):
            item = self.items[i-1]
            money_for_item = item.sell()
            if item.amount <= 0:
                self.items.pop(i-1)
            return money_for_item
        return 0

    def equip_item(self):
        print("\n装备什么? ['0' 退出]") # 从库存中装备某件物品（必须是“装备”类型）
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
            return None
        elif i <= len(self.items):
            item = self.items[i-1]
            if type(item) == Equipment:
                self.items.pop(i-1)
                return item
            else:
                print("选择一个可装备的物品")
                return None

    def use_item(self):
        print("\n使用什么? ['0' 退出]") # 使用特定类型的“消耗品”物品
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
            return None
        elif i <= len(self.items):
            item = self.items[i-1]
            if item.object_type == "consumable":
                item.amount -= 1
                if item.amount <= 0:
                    self.items.pop(i-1)
                return item
            else:
                print("选择一个消耗品")
                return None

    @property
    def total_worth(self):
        total_worth = sum(item.amount * item.individual_value for item in self.items)
        return total_worth

class Item():
    def __init__(self, name, description, amount, individual_value, object_type) -> None:
        self.name = name
        self.description = description
        self.amount = amount
        self.individual_value = individual_value
        self.object_type = object_type

    def drop(self):
        if self.amount == 1:
            print(f"丢弃了一个 {self.name}.\n当前背包:")
            self.amount -= 1
        else:
            print(f"有 {self.amount} 个 {self.name}, 丢弃多少?")
            amount_to_drop = int(input("> "))
            if 0 < amount_to_drop <= self.amount:
                self.amount -= amount_to_drop
                print(f"丢弃了 {self.name}x{amount_to_drop}.\n当前背包:")
            else:
                print("数量无效!")

    def sell(self):
        if self.amount == 1:
            self.amount -= 1
            print(f"出售了一个 {self.name}, 得 {self.individual_value}")
            return self.individual_value
        elif self.amount > 1:
            print(f"有 {self.amount} 个 {self.name}, 出售多少?")
            amount_to_sell = int(input("> "))
            if 0 < amount_to_sell <= self.amount:
                money_to_receive = self.individual_value * amount_to_sell
                self.amount -= amount_to_sell
                print(f"售出 {self.name}x{amount_to_sell}, 得 {money_to_receive}")
                return money_to_receive
            else:
                print("数量无效!")
        return 0

    def add_to_inventory(self, inventory):
        for item in inventory.items:
            if self.name == item.name:
                item.amount += self.amount
                break
        else:
            inventory.items.append(self)
            print(f"{self.name}x{self.amount} 已放入背包!")

    def show_info(self):
        return f"[x{self.amount}] {self.name} ({self.object_type})"

class Equipment(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat_change_list):
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat_change_list = stat_change_list

    def show_info(self):
        return f"[x{self.amount}] {self.name} ({self.object_type}) {self.show_stats()}"

    def show_stats(self):
        stats_string = "[ "
        for stat in self.stat_change_list:
            sign = "+"
            if self.stat_change_list[stat] < 0:
                sign = ""
            stats_string += f"{stat} {sign}{self.stat_change_list[stat]} "
        stats_string += "]"
        return stats_string

class Potion(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat, amount_to_change) -> None:
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat == "hp":
            combat.heal(caster, self.amount_to_change)
        elif self.stat == "mp":
            combat.recover_mp(caster, self.amount_to_change)
