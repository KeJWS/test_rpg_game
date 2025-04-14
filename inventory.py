import test.fx as fx

class Inventory():
    def __init__(self) -> None:
        self.items = []

    def show_inventory(self):
        print(f"总价值: {self.total_worth}")
        for index, item in enumerate(self.items, start=1):
            print(f"{index} - {item.show_info()}")

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
            print('现在你的背包如下：')
            self.show_inventory()

    def sell_item(self):
        print("\n出售什么? ['0' 退出]")
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
            return 0
        elif i <= len(self.items):
            item = self.items[i-1]
            money_for_item, amount_to_sell = item.sell()
            self.decrease_item_amount(item, amount_to_sell)
            return money_for_item
        else:
            print("关闭背包...")
            return 0

    def equip_item(self):
        print("\n装备什么? ['0' 退出]")
        self.show_inventory()
        i = int(input("> "))
        if i == 0:
            print("关闭背包...")
            return None
        elif i <= len(self.items):
            item = self.items[i-1]
            if isinstance(item, Equipment):
                return item
            else:
                print("选择一个可装备的物品")
                return None

    def use_item(self):
        print("\n使用什么? ['0' 退出]")
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

    def decrease_item_amount(self, item, amount):
        for actual_item in self.items:
            if item.name == actual_item.name:
                actual_item.amount -= amount
                if actual_item.amount <= 0:
                    self.items.remove(actual_item)

    def add_item(self, item):
        item.add_to_inventory_player(self)

    @property
    def total_worth(self):
        total_worth = sum(item.amount * item.individual_value for item in self.items)
        return total_worth

    def view_item(self):
        if not self.items:
            print("背包为空。")
            return None
        print("选择一个物品查看详情：")
        self.show_inventory()
        while True:
            choice = input("输入编号 (或 0 取消):")
            if choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    return None
                elif 1 <= choice <= len(self.items):
                    return self.items[choice - 1]
            print("无效输入")

class Item():
    def __init__(self, name, description, amount, individual_value, object_type) -> None:
        self.name = name
        self.description = description
        self.amount = amount
        self.individual_value = individual_value
        self.object_type = object_type

    def drop(self):
        if self.amount == 1:
            print(f"丢弃了一个 {self.name}")
            self.amount -= 1
        else:
            print(f"有 {self.amount} 个 {self.name}, 丢弃多少?")
            amount_to_drop = int(input("> "))
            if 0 < amount_to_drop <= self.amount:
                self.amount -= amount_to_drop
                print(f"丢弃了 {self.name}x{amount_to_drop}")
            else:
                print("数量无效!")

    def sell(self):
        if self.amount == 1:
            money_to_receive = int(round(self.individual_value * 0.5))
            print(f"快速售出 {self.name}x1, 获得 {money_to_receive}G")
            return money_to_receive, 1
        elif self.amount > 1:
            print(f"有 {self.amount} 个 {self.name}, 出售多少?")
            amount_to_sell = int(input("> "))
            if 0 < amount_to_sell <= self.amount:
                # 物品售价为其价值的 50%
                money_to_receive = int(round(self.individual_value * 0.5 * amount_to_sell))
                print(f"您确定要以 {money_to_receive}G 的价格出售 {amount_to_sell} {self.name} 吗? [y/n]")
                confirmation = input("> ")
                if confirmation == "y":
                    print(f"售出 {self.name}x{amount_to_sell}, 得 {money_to_receive}")
                    return money_to_receive, amount_to_sell
                else:
                    pass
            else:
                print(f"没有那么多{self.name}")
        return 0, 0

    def buy(self, player):
        if self.amount > 1:
            print("买多少?")
            amount_to_buy = int(input("> "))
            price = self.individual_value * amount_to_buy
            if amount_to_buy > self.amount:
                print(f"商人没有那么多 {self.name}")
            elif price > player.money:
                print("没有足够的钱")
            else:
                item_for_player = self.clone(amount_to_buy)
                self.amount -= amount_to_buy
                item_for_player.add_to_inventory_player(player.inventory)
                player.money -= price
        elif self.amount == 1 and self.individual_value <= player.money:
            item_for_player = self.clone(1)
            item_for_player.add_to_inventory_player(player.inventory)
            player.money -= self.individual_value
            self.amount = 0
        else:
            print("没有足够的钱")

    def clone(self, amount):
        return Item(self.name, self.description, amount, self.individual_value, self.object_type)

    def add_to_inventory_player(self, inventory):
        amount_added = self.amount
        self.add_to_inventory(inventory, amount_added)
        print(f"{amount_added} 个 {fx.YELLO}{self.name}{fx.END} 已添加到库存")

    def add_to_inventory(self, inventory, amount):
        already_in_inventory = False
        for item in inventory.items:
            if self.name == item.name:
                item.amount += amount
                already_in_inventory = True
                break
        if not already_in_inventory:
            self.amount = amount
            inventory.items.append(self)

    def show_info(self):
        return f"[x{self.amount}] {self.name} ({self.object_type}) - {self.individual_value}"

    def get_detailed_info(self):
        info = f"名称: {self.name}\n"
        info += f"类型: {self.object_type}\n"
        info += f"价值: {fx.YELLO}{self.individual_value}G{fx.END}\n"
        info += f"描述: {self.description}\n"
        info += f"数量: x{self.amount}\n"

        return info

class Equipment(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat_change_list, combo):
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat_change_list = stat_change_list
        self.combo = combo
        self.durability = 100  # 耐久度
        self.max_durability = 100
        self.level = 0  # 装备等级

    def show_info(self):
        combo_name = fx.yellow(self.combo.name) if self.combo else ""
        return (
            f"[x{self.amount}] {self.name} ({self.object_type}) {self.show_stats()} - {self.individual_value}G {combo_name}\n"
            f"    简介: {self.description}"
        )

    def show_stats(self):
        stats_string = "[ "
        for stat in self.stat_change_list:
            sign = "+"
            if self.stat_change_list[stat] < 0:
                sign = ""
            stats_string += f"{stat} {sign}{self.stat_change_list[stat]} "
        stats_string += "]"
        return fx.green(stats_string)

    def get_detailed_info(self):
        info = super().get_detailed_info()
        info += f"装备等级: +{self.level}\n"
        info += f"耐久度: {self.durability}/{self.max_durability}\n"
        info += "属性加成:\n"

        for stat, value in self.stat_change_list.items():
            sign = "+" if value >= 0 else ""
            info += f"  {fx.GREEN}{stat}: {sign}{value}{fx.END}\n"

        return info

    def clone(self, amount):
        return Equipment(self.name, self.description, amount, self.individual_value, self.object_type, self.stat_change_list, self.combo)

class Potion(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat, amount_to_change) -> None:
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat == "hp":
            caster.heal(self.amount_to_change)
        elif self.stat == "mp":
            caster.recover_mp(self.amount_to_change)

    def clone(self, amount):
        return Potion(self.name, self.description, amount, self.individual_value, self.object_type, self.stat, self.amount_to_change)

class Grimoire(Item):
    def __init__(self, name, description, amount, individual_value, object_type, spell) -> None:
        super().__init__(name, description, amount, individual_value, object_type)
        self.spell = spell

    def activate(self, caster):
        already_learnt = False
        for skill in caster.spells:
            if skill.name == self.spell.name:
                already_learnt = True
                break
        if already_learnt:
            print("你已经知道这个咒语")
        else:
            print(f"阅读 {self.name}, 你学会了释放: {self.spell.name}")
            caster.spells.append(self.spell)

    def clone(self, amount):
        return Grimoire(self.name, self.description, amount, self.individual_value, self.object_type, self.spell)

class Jewel(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat, amount_to_change) -> None:
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat in caster.stats:
            caster.stats[self.stat] += self.amount_to_change

    def clone(self, amount):
        return Jewel(self.name, self.description, amount, self.individual_value, self.object_type, self.stat, self.amount_to_change)
