
class Inventory():

    def __init__(self) -> None:
        self.items = []

    def show_inventory(self):
        index = 1
        for item in self.items:
            print(str(f"{index} - {item.name}x{item.amount}"))
            index += 1

    def drop_item(self):
        print("\n丢掉什么? ['0' 退出]")
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
        elif i <= len(self.items):
            item = self.items[i-1]
            item.drop()
            if item.amount <= 0:
                self.items.pop(i-1)
            self.show_inventory()

    def sell_item(self):
        print("\n出售什么? ['0' 退出]")
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
        elif i <= len(self.items):
            item = self.items[i-1]
            money_for_item = item.sell()
            if item.amount <= 0:
                self.items.pop(i-1)
            return money_for_item

    def equip_item(self):
        print("\n装备什么? ['0' 退出]")
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
                return None

    @property
    def total_worth(self):
        total_worth = 0
        for item in self.items:
            total_worth += item.amount * item.individual_value
        print(f"总价值: {total_worth}")

class Item():

    def __init__(self, name, description, amount, individual_value) -> None:
        self.name = name
        self.description = description
        self.amount = amount
        self.individual_value = individual_value

    @property
    def total_worth(self):
        return self.amount * self.individual_value

    def drop(self):
        if self.amount == 1:
            print(f"丢弃了一个 {self.name}.\n当前背包:")
            self.amount -= 1
        else:
            print(f"有 {self.amount} 个, 丢弃多少？")
            amount_to_drop = int(input("> "))
            if amount_to_drop > self.amount:
                print("物品不够")
            else:
                self.amount -= amount_to_drop
                print(f"丢弃 {self.name}x{amount_to_drop}.\n当前背包:")

    def sell(self):
        if self.amount >= 1:
            print("卖多少?")
            amount_to_sell = int(input("> "))
            if amount_to_sell <= self.amount and amount_to_sell != 0:
                money_to_receive = self.individual_value * amount_to_sell
                print(f"即将出售 {self.name}x{amount_to_sell}, 赚 {money_to_receive} ? [y/n]")
                confirmation = input("> ")
                if confirmation == "y":
                    self.amount -= amount_to_sell
                    print(f"售出 {self.name}x{amount_to_sell} 得 {money_to_receive}")
                    return money_to_receive
                else:
                    pass
            else:
                print("数量不足!")
        return 0

    def add_to_inventory(self, inventory):
        already_in_inventory = False
        for item in inventory.items:
            if self.name == item.name:
                item.amount += self.amount
                already_in_inventory = True
        if not already_in_inventory:
            inventory.items.append(self)
        print(f"{self.name}x{self.amount} 已放入背包!")

class Equipment(Item):
    def __init__(self, name, description, amount, individual_value, stat_change_list, equipment_type):
        super().__init__(name, description, amount, individual_value)
        self.stat_change_list = stat_change_list
        self.equipment_type = equipment_type
