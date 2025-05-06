from rich.console import Console
import test.fx as fx
console = Console()

def prompt_for_amount(max_amount, prompt="多少个？") -> int:
    """提示用户输入数量并进行验证"""
    try:
        amount = int(input(f"{prompt} (最多: {max_amount})\n> "))
        if 0 < amount <= max_amount:
            return amount
        print(f"请输入 1 到 {max_amount} 之间的数字!")
    except ValueError:
        print("请输入有效数字!")
    return 0

class Item:
    def __init__(self, name, description, amount, individual_value, object_type):
        self.name = name
        self.description = description
        self.amount = amount
        self.individual_value = individual_value
        self.object_type = object_type

    def _get_valid_amount(self, prompt_text) -> int:
        """统一处理数量输入和验证"""
        return prompt_for_amount(self.amount, prompt_text)

    def drop(self):
        if self.amount == 1:
            console.print(f"丢弃了一个 {self.name}")
            self.amount -= 1
            return 1
        amount_to_drop = self._get_valid_amount("丢弃多少?")
        if amount_to_drop > 0:
            self.amount -= amount_to_drop
            console.print(f"丢弃了 {self.name}x{amount_to_drop}")
            return amount_to_drop
        return 0

    def sell(self):
        if self.amount == 1:
            price = int(round(self.individual_value * 0.5))
            console.print(f"快速售出 {self.name}x1, 获得 {price}G")
            return price, 1

        amount_to_sell = self._get_valid_amount("出售多少?")
        if amount_to_sell <= 0:
            print("取消出售")
            return 0, 0

        price = int(round(self.individual_value * 0.5 * amount_to_sell))
        confirmation = input(f"您确定要以 {price}G 的价格出售 {amount_to_sell} 个 {self.name} 吗? [y/n]\n> ").lower()
        if confirmation == "y":
            console.print(f"售出 {self.name}x{amount_to_sell}, 得 {price}")
            return price, amount_to_sell

        print("取消出售")
        return 0, 0

    def buy(self, player):
        if self.amount > 1:
            amount_to_buy = self._get_valid_amount("买多少?")
            if amount_to_buy <= 0:
                print("取消购买")
                return
            total_price = self.individual_value * amount_to_buy
            if total_price > player.money:
                print("没有足够的钱")
                return
        else:
            amount_to_buy, total_price = 1, self.individual_value
            if total_price > player.money:
                print("没有足够的钱")
                return

        item_for_player = self.clone(amount_to_buy)
        self.amount -= amount_to_buy
        item_for_player.add_to_inventory_player(player.inventory)
        player.money -= total_price
        console.print(f"💰: {player.money}")

    def add_to_inventory_player(self, inventory):
        """添加至玩家背包"""
        amount_added = self.amount
        self.add_to_inventory(inventory, amount_added)
        console.print(f"{amount_added} 个 [yellow]{self.name}[/yellow] 已添加到库存")

    def add_to_inventory(self, inventory, amount):
        """添加至背包系统，如果已有则叠加"""
        for item in inventory.items:
            if self.name == item.name:
                item.amount += amount
                return
        new_item = self.clone(amount)
        inventory.items.append(new_item)

    def show_info(self):
        return f"[x{self.amount}] {self.name} ({self.object_type}) - {self.individual_value}G"

    def get_detailed_info(self):
        return (
            f"\n名称: {self.name}\n"
            f"类型: {self.object_type}\n"
            f"价值: {fx.YELLO}{self.individual_value}G{fx.END}\n"
            f"描述: {self.description}\n"
            f"数量: x{self.amount}\n"
        )

    def clone(self, amount):
        return Item(self.name, self.description, amount, self.individual_value, self.object_type)

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
    def __init__(self, name, description, amount, individual_value, stat, amount_to_change) -> None:
        super().__init__(name, description, amount, individual_value, "consumable")
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat in caster.stats:
            caster.stats[self.stat] += self.amount_to_change
            fx.typewriter(fx.yellow(f"{self.stat} 增加了 {self.amount_to_change} 点"))

    def clone(self, amount):
        return Jewel(self.name, self.description, amount, self.individual_value, self.stat, self.amount_to_change)

class Food(Item):
    def __init__(self, name, description, amount, individual_value, hunger_restore, hp_restore=0, mp_restore=0) -> None:
        super().__init__(name, description, amount, individual_value, "food")
        self.hunger_restore = hunger_restore
        self.hp_restore = hp_restore
        self.mp_restore = mp_restore

    def activate(self, player):
        """使用食物, 恢复饱食度、HP/MP"""
        print(f"{player.name} 吃了一个 {self.name}")
        old_hunger = player.stats["hunger"]
        player.stats["hunger"] = min(player.stats["max_hunger"], player.stats["hunger"] + self.hunger_restore)
        hunger_restored = player.stats["hunger"] - old_hunger
        print(f"饱食度恢复了 {hunger_restored} 点 ({player.stats["hunger"]}/{player.stats["max_hunger"]})")

        if self.hp_restore > 0:
            player.heal(self.hp_restore)
        elif self.hp_restore < 0:
            player.take_dmg(abs(self.hp_restore))
        if self.mp_restore > 0:
            player.recover_mp(self.mp_restore)

    def get_detailed_info(self):
        """显示食物的详细信息"""
        base_info = super().get_detailed_info()
        food_info = f"饱食度: +{self.hunger_restore}\n"
        if self.hp_restore > 0:
            food_info += f"生命值: +{self.hp_restore}\n"
        if self.mp_restore > 0:
            food_info += f"魔法值: +{self.mp_restore}\n"
        return base_info + food_info

    def clone(self, amount):
        return Food(self.name, self.description, amount, self.individual_value, self.hunger_restore, self.hp_restore, self.mp_restore)
