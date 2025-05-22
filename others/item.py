"""
物品系统模块，定义游戏中的各种物品类型及其行为。

该模块实现了游戏中的物品系统，包括基本物品类(Item)及其衍生的特殊物品类型，
如药水(Potion)、魔法书(Grimoire)、宝石(Jewel)和食物(Food)。每种物品类型
都有其特定的属性和使用效果，支持物品的使用、出售、购买和丢弃等基本操作。
"""

from rich.console import Console
from ui import typewriter

console = Console()

def prompt_for_amount(max_amount, prompt="多少个？") -> int:
    """
    提示用户输入数量并进行验证。

    向用户显示提示信息并要求输入一个数量，确保输入的数量在有效范围内。

    参数:
        max_amount (int): 允许的最大数量
        prompt (str): 显示给用户的提示信息，默认为"多少个？"

    返回:
        int: 用户输入的有效数量，如果输入无效则返回0

    异常:
        不会抛出异常，输入无效时会捕获ValueError并返回0
    """
    try:
        amount = int(input(f"{prompt} (最多: {max_amount})\n> "))
        if 0 < amount <= max_amount:
            return amount
        print(f"请输入 1 到 {max_amount} 之间的数字!")
    except ValueError:
        print("请输入有效数字!")
    return 0

class Item:
    """
    物品基类，定义所有物品的基本属性和方法。

    实现了物品的基本功能，包括物品的丢弃、出售、购买和添加到背包等操作。
    作为其他特殊物品类型的父类，提供通用的物品处理逻辑。

    属性:
        name (str): 物品名称
        description (str): 物品描述
        amount (int): 物品数量
        individual_value (int): 物品单价
        object_type (str): 物品类型
    """
    def __init__(self, name, description, amount, individual_value, object_type):
        """
        初始化物品实例。

        设置物品的基本属性。

        参数:
            name (str): 物品名称
            description (str): 物品描述
            amount (int): 物品数量
            individual_value (int): 物品单价（游戏内货币）
            object_type (str): 物品类型标识符
        """
        self.name = name
        self.description = description
        self.amount = amount
        self.individual_value = individual_value
        self.object_type = object_type

    def _get_valid_amount(self, prompt_text) -> int:
        """
        统一处理数量输入和验证。

        提示用户输入数量并确保输入有效，是一个内部辅助方法。

        参数:
            prompt_text (str): 显示给用户的提示信息

        返回:
            int: 用户输入的有效数量，如果输入无效则返回0
        """
        return prompt_for_amount(self.amount, prompt_text)

    def drop(self):
        """
        丢弃物品。

        如果物品数量为1，直接丢弃；否则提示用户输入要丢弃的数量。

        返回:
            int: 实际丢弃的物品数量

        副作用:
            - 减少物品的数量
            - 输出丢弃信息
        """
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
        """
        出售物品。

        如果物品数量为1，直接出售；否则提示用户输入要出售的数量，
        并要求确认交易。出售价格为物品价值的50%。

        返回:
            tuple: (获得的金钱, 出售的数量)

        副作用:
            - 输出出售信息
            - 注意：此方法不会自动减少物品数量，需要调用者处理
        """
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
        """
        购买物品。

        处理玩家购买物品的逻辑，检查金钱是否足够，
        如果成功购买，将物品添加到玩家背包并扣除金钱。

        参数:
            player: 玩家对象，包含金钱和背包属性

        副作用:
            - 减少店铺物品数量
            - 向玩家背包添加物品
            - 减少玩家金钱
            - 输出购买信息
        """
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
        """
        添加物品至玩家背包。

        将当前物品添加到玩家背包，并显示添加信息。

        参数:
            inventory: 玩家的背包对象


        副作用:
            - 向背包添加物品
            - 输出添加信息
        """
        amount_added = self.amount
        self.add_to_inventory(inventory, amount_added)
        console.print(f"{amount_added} 个 [yellow]{self.name}[/yellow] 已添加到库存")

    def add_to_inventory(self, inventory, amount):
        """
        添加物品至背包系统。

        如果背包中已有同名物品，则增加数量；否则创建新物品添加到背包。

        参数:
            inventory: 目标背包对象
            amount (int): 要添加的数量

        副作用:
            - 增加背包中现有物品数量或添加新物品到背包
        """
        for item in inventory.items:
            if self.name == item.name:
                item.amount += amount
                return
        new_item = self.clone(amount)
        inventory.items.append(new_item)

    def show_info(self):
        """
        获取物品的简要信息。

        返回物品的基本信息字符串，包括数量、名称、类型和价值。

        返回:
            str: 格式化的物品信息字符串
        """
        return f"[x{self.amount}] {self.name} ({self.object_type}) - {self.individual_value}G"

    def get_detailed_info(self):
        """
        获取物品的详细信息。

        返回包含物品所有属性的详细信息字符串。

        返回:
            str: 格式化的物品详细信息字符串
        """
        return (
            f"\n名称: {self.name}\n"
            f"类型: {self.object_type}\n"
            f"价值: \033[33m{self.individual_value}G\033[0m\n"
            f"描述: {self.description}\n"
            f"数量: x{self.amount}\n"
        )

    def clone(self, amount):
        """
        创建物品的克隆。

        创建一个新的物品实例，具有相同的属性但可能不同的数量。

        参数:
            amount (int): 新物品实例的数量

        返回:
            Item: 新创建的物品实例
        """
        return Item(self.name, self.description, amount, self.individual_value, self.object_type)

class Potion(Item):
    """
    药水类，可恢复生命值或魔法值的消耗品。

    继承自Item类，添加了特定属性来定义药水的效果。

    属性:
        stat (str): 要恢复的属性，如"hp"或"mp"
        amount_to_change (int): 恢复的数量
    """
    def __init__(self, name, description, amount, individual_value, object_type, stat, amount_to_change) -> None:
        """
        初始化药水实例。

        设置药水的基本属性和特定的恢复效果。

        参数:
            name (str): 药水名称
            description (str): 药水描述
            amount (int): 药水数量
            individual_value (int): 药水单价
            object_type (str): 物品类型标识符
            stat (str): 要恢复的属性，如"hp"或"mp"
            amount_to_change (int): 恢复的数量
        """
        super().__init__(name, description, amount, individual_value, object_type)
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        """
        使用药水。

        根据药水类型恢复施用者的生命值或魔法值。

        参数:
            caster: 使用药水的战斗单位或玩家

        副作用:
            - 恢复施用者的HP或MP
            - 输出使用信息
        """
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat == "hp":
            caster.heal(self.amount_to_change)
        elif self.stat == "mp":
            caster.recover_mp(self.amount_to_change)

    def clone(self, amount):
        return Potion(self.name, self.description, amount, self.individual_value, self.object_type, self.stat, self.amount_to_change)

class Grimoire(Item):
    """
    魔法书类，可用于学习法术的物品。

    继承自Item类，添加了法术属性以定义可学习的技能。

    属性:
        spell: 魔法书包含的法术对象
    """
    def __init__(self, name, description, amount, individual_value, object_type, spell) -> None:
        """
        初始化魔法书实例。

        设置魔法书的基本属性和包含的法术。

        参数:
            name (str): 魔法书名称
            description (str): 魔法书描述
            amount (int): 魔法书数量
            individual_value (int): 魔法书单价
            object_type (str): 物品类型标识符
            spell: 魔法书包含的法术对象
        """
        super().__init__(name, description, amount, individual_value, object_type)
        self.spell = spell

    def activate(self, caster):
        """
        使用魔法书学习法术。

        检查施用者是否已经学会该法术，如果没有则学习新法术。

        参数:
            caster: 使用魔法书的战斗单位或玩家

        副作用:
            - 可能向施用者的法术列表添加新法术
            - 输出学习结果信息
        """
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
    """
    宝石类，可永久提升属性的消耗品。

    继承自Item类，添加了特定属性来定义宝石的效果。

    属性:
        stat (str): 要提升的属性名称
        amount_to_change (int): 属性提升的数量
    """
    def __init__(self, name, description, amount, individual_value, stat, amount_to_change) -> None:
        """
        初始化宝石实例。

        设置宝石的基本属性和特定的属性提升效果。

        参数:
            name (str): 宝石名称
            description (str): 宝石描述
            amount (int): 宝石数量
            individual_value (int): 宝石单价
            stat (str): 要提升的属性名称
            amount_to_change (int): 属性提升的数量
        """
        super().__init__(name, description, amount, individual_value, "consumable")
        self.stat = stat
        self.amount_to_change = amount_to_change

    def activate(self, caster):
        """
        使用宝石提升属性。

        永久提升施用者指定属性的数值。

        参数:
            caster: 使用宝石的战斗单位或玩家

        副作用:
            - 永久增加施用者的某项属性
            - 输出提升信息
        """
        print(f"{caster.name} 使用了一个 {self.name}")
        if self.stat in caster.stats:
            caster.stats[self.stat] += self.amount_to_change
            typewriter(f"\033[33m{self.stat} 增加了 {self.amount_to_change} 点\033[0m")

    def clone(self, amount):
        return Jewel(self.name, self.description, amount, self.individual_value, self.stat, self.amount_to_change)

class Food(Item):
    """
    食物类，可恢复饱食度和可能恢复生命值或魔法值的消耗品。

    继承自Item类，添加了特定属性来定义食物的效果。

    属性:
        hunger_restore (int): 恢复的饱食度
        hp_restore (int): 恢复的生命值
        mp_restore (int): 恢复的魔法值
    """
    def __init__(self, name, description, amount, individual_value, hunger_restore, hp_restore=0, mp_restore=0) -> None:
        """
        初始化食物实例。

        设置食物的基本属性和特定的恢复效果。

        参数:
            name (str): 食物名称
            description (str): 食物描述
            amount (int): 食物数量
            individual_value (int): 食物单价
            hunger_restore (int): 恢复的饱食度
            hp_restore (int, optional): 恢复的生命值，默认为0
            mp_restore (int, optional): 恢复的魔法值，默认为0
        """
        super().__init__(name, description, amount, individual_value, "food")
        self.hunger_restore = hunger_restore
        self.hp_restore = hp_restore
        self.mp_restore = mp_restore

    def activate(self, player):
        """
        使用食物恢复饱食度和可能的HP/MP。

        恢复玩家的饱食度，并根据食物属性可能恢复生命值或魔法值。

        参数:
            player: 使用食物的玩家

        副作用:
            - 恢复玩家的饱食度
            - 可能恢复玩家的HP或MP
            - 输出恢复信息
        """
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
        """
        获取食物的详细信息。

        扩展基类的详细信息方法，添加食物特有的属性信息。

        返回:
            str: 格式化的食物详细信息字符串，包括饱食度和可能的HP/MP恢复值
        """
        base_info = super().get_detailed_info()
        food_info = f"饱食度: +{self.hunger_restore}\n"
        if self.hp_restore > 0:
            food_info += f"生命值: +{self.hp_restore}\n"
        if self.mp_restore > 0:
            food_info += f"魔法值: +{self.mp_restore}\n"
        return base_info + food_info

    def clone(self, amount):
        return Food(self.name, self.description, amount, self.individual_value, self.hunger_restore, self.hp_restore, self.mp_restore)
