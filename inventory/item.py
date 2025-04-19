import test.fx as fx
import inventory.utils as utils

class Item:
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
            return 1
        else:
            print(f"有 {self.amount} 个 {self.name}")
            amount_to_drop = utils.prompt_for_amount(self.amount, "丢弃多少?")
            if amount_to_drop > 0:
                self.amount -= amount_to_drop
                print(f"丢弃了 {self.name}x{amount_to_drop}")
                return amount_to_drop
        return 0

    def sell(self):
        if self.amount == 1:
            money_to_receive = int(round(self.individual_value * 0.5))
            print(f"快速售出 {self.name}x1, 获得 {money_to_receive}G")
            return money_to_receive, 1
        elif self.amount > 1:
            print(f"有 {self.amount} 个 {self.name}")
            amount_to_sell = utils.prompt_for_amount(self.amount, "出售多少?")
            if amount_to_sell > 0:
                money_to_receive = int(round(self.individual_value * 0.5 * amount_to_sell))
                print(f"您确定要以 {money_to_receive}G 的价格出售 {amount_to_sell} {self.name} 吗? [y/n]")
                confirmation = input("> ")
                if confirmation.lower() == "y":
                    print(f"售出 {self.name}x{amount_to_sell}, 得 {money_to_receive}")
                    return money_to_receive, amount_to_sell
                else:
                    print("取消出售")
            else:
                print("取消出售")
        return 0, 0

    def buy(self, player):
        if self.amount > 1:
            amount_to_buy = utils.prompt_for_amount(self.amount, "买多少?")
            if amount_to_buy <= 0:
                print("取消购买")
                return

            price = self.individual_value * amount_to_buy
            if price > player.money:
                print("没有足够的钱")
                return

            item_for_player = self.clone(amount_to_buy)
            self.amount -= amount_to_buy
            item_for_player.add_to_inventory_player(player.inventory)
            player.money -= price
            print(f"💰: {player.money}")
        elif self.amount == 1:
            if self.individual_value <= player.money:
                item_for_player = self.clone(1)
                item_for_player.add_to_inventory_player(player.inventory)
                player.money -= self.individual_value
                self.amount = 0
                print(f"💰: {player.money}")
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
        return f"[x{self.amount}] {self.name} ({self.object_type}) - {self.individual_value}G"

    def get_detailed_info(self):
        info = f"名称: {self.name}\n"
        info += f"类型: {self.object_type}\n"
        info += f"价值: {fx.YELLO}{self.individual_value}G{fx.END}\n"
        info += f"描述: {self.description}\n"
        info += f"数量: x{self.amount}\n"
        return info

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
            fx.typewriter(fx.yellow(f"{self.stat} 增加了 {self.amount_to_change} 点"))

    def clone(self, amount):
        return Jewel(self.name, self.description, amount, self.individual_value, self.object_type, self.stat, self.amount_to_change)
