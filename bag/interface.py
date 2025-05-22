"""
物品库存界面模块，提供与库存系统交互的用户界面。

该模块实现了库存系统的交互界面，包括物品显示、选择、使用、装备、
丢弃、出售和比较等功能。提供了用户友好的命令行界面，便于玩家
管理其库存中的各类物品和装备。
"""

from rich.console import Console

from ui import fx
from ui.clear_screen import clear_screen

console = Console()

def select_item_from_list(item_list, prompt="选择一个物品:", allow_exit=True):
    """
    显示物品列表并让用户选择其中一个。

    在控制台中展示物品列表，每个物品以编号和信息形式显示，
    等待用户输入编号选择一个物品。支持退出选择过程。

    参数:
        item_list (list): 要显示的物品列表
        prompt (str, optional): 显示给用户的提示文本，默认为"选择一个物品:"
        allow_exit (bool, optional): 是否允许用户退出选择，默认为True

    返回:
        object|None: 用户选择的物品对象，如果用户退出则返回None
    """
    if not item_list:
        print("没有可选择的物品")
        return None

    print(f"\n{prompt} {['', '[输入 0 退出]'][allow_exit]}")
    for index, item in enumerate(item_list, start=1):
        console.print(f"{index}. {item.show_info()}")

    while True:
        choice = input("> ")
        if choice == "0" and allow_exit:
            print("退出...")
            return None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(item_list):
                return item_list[choice_num - 1]
        print("无效输入")

class InventoryInterface:
    """
    库存界面类，提供与物品库存交互的用户界面。

    处理游戏中与库存相关的所有用户交互，包括显示、使用、丢弃、
    出售物品以及装备管理等功能。为库存系统提供了一个命令行界面，
    便于玩家管理其拥有的物品。

    属性:
        inventory: 与此界面关联的库存对象
    """
    def __init__(self, inventory):
        """
        初始化库存界面实例。

        创建一个新的库存界面对象，关联指定的库存对象。

        参数:
            inventory: 需要管理的库存对象
        """
        self.inventory = inventory

    def show_inventory(self):
        """
        显示库存内容。

        以表格形式展示库存中所有物品，并显示容量摘要信息。
        """
        print(f"{fx.BOLD_UNDERLINED}背包内容:{fx.END}")
        table_panel, summary_text = self.inventory.get_formatted_inventory_table()
        console.print(table_panel)
        console.print(summary_text)

    def drop_item(self):
        """
        丢弃库存中的物品。

        显示库存内容，提示用户选择要丢弃的物品，执行丢弃操作并更新库存。
        如果物品数量变为0，则从库存中完全移除该物品。

        副作用:
            - 减少或移除库存中的物品
            - 刷新屏幕
            - 更新并显示库存内容
            - 在控制台输出操作结果信息

        异常处理:
            捕获无效输入导致的ValueError异常并提供友好提示
        """
        if not self.inventory.items:
            print("背包是空的，没有可丢弃的物品")
            return
        print("\n丢掉什么? ['0' 退出]")
        self.show_inventory()
        try:
            i = int(input("> "))
            if i == 0:
                print("关闭背包...")
                return
            elif 1 <= i <= len(self.inventory.items):
                item = self.inventory.items[i-1]
                dropped_amount = item.drop()
                if item.amount <= 0:
                    self.inventory.items.pop(i-1)
                clear_screen()
                self.show_inventory()
            else:
                print("无效的选择!")
        except ValueError:
            print("请输入有效数字!")

    def sell_item(self):
        """
        出售库存中的物品。

        显示库存内容，提示用户选择要出售的物品，执行出售操作并更新库存。
        返回出售物品获得的金钱数量。

        返回:
            int: 出售物品获得的金钱，失败则返回0

        副作用:
            - 减少库存中的物品数量
            - 可能从库存中移除物品（如果数量变为0）
            - 在控制台输出操作结果信息

        异常处理:
            捕获无效输入导致的ValueError异常并提供友好提示
        """
        if not self.inventory.items:
            print("背包是空的，没有可出售的物品")
            return 0
        print("\n出售什么? ['0' 退出]")
        self.show_inventory()
        try:
            i = int(input("> "))
            if i == 0:
                print("关闭背包...")
                return 0
            elif 1 <= i <= len(self.inventory.items):
                item = self.inventory.items[i-1]
                money_for_item, amount_to_sell = item.sell()
                self.inventory.decrease_item_amount(item, amount_to_sell)
                return money_for_item
            else:
                print("无效的选择!")
                return 0
        except ValueError:
            print("请输入有效数字!")
            return 0

    def equip_item(self):
        """
        选择并返回要装备的物品。

        从库存中筛选出所有可装备的物品，显示给用户选择一个装备。
        不实际执行装备操作，仅返回选中的装备物品。

        返回:
            object|None: 用户选择的装备物品，如果没有装备或用户取消则返回None

        副作用:
            在控制台输出装备选择界面或无装备提示信息
        """
        equipments = self.inventory.get_equipments()
        if not equipments:
            print("背包中没有可装备的物品")
            return None
        return select_item_from_list(equipments, "装备什么?")

    def use_item(self):
        """
        选择并使用消耗品物品。

        从库存中筛选出所有可使用的消耗品和食物，让用户选择一个使用。
        选择后自动减少物品数量，并返回使用的物品对象。

        返回:
            object|None: 用户使用的物品对象，如果没有可用物品或用户取消则返回None

        副作用:
            - 减少库存中选中物品的数量
            - 可能从库存中移除物品（如果数量变为0）
            - 在控制台输出物品选择界面或无可用物品提示
        """
        consumables = self.inventory.get_items_by_type("consumable")
        consumables += self.inventory.get_items_by_type("food")
        if not consumables:
            print("背包中没有可使用的物品")
            return None
        item = select_item_from_list(consumables, "使用什么?")
        if item:
            self.inventory.decrease_item_amount(item, 1)
            return item
        return None

    def view_item(self):
        """
        查看物品详情。

        显示库存内容，让用户选择一个物品以查看其详细信息。
        不改变库存状态，仅返回选中的物品对象。

        返回:
            object|None: 用户选择查看的物品对象，如果背包为空或用户取消则返回None

        副作用:
            在控制台输出物品选择界面或空背包提示
        """
        if not self.inventory.items:
            print("背包为空")
            return None
        print(f"{fx.BOLD}选择一个物品查看详情:{fx.END}")
        self.show_inventory()
        while True:
            choice = input("输入编号 (或 0 取消): ")
            if choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    return None
                elif 1 <= choice <= len(self.inventory.items):
                    item = self.inventory.items[choice - 1]
                    return item
            print("无效输入")

    def compare_equipment(self):
        """
        比较两件装备的属性。

        从库存中筛选出所有装备，让用户选择两件进行属性比较。
        显示两件装备的详细比较信息。

        副作用:
            - 在控制台显示装备选择界面
            - 清空屏幕
            - 显示装备比较结果
        """
        equipments = self.inventory.get_equipments()
        if len(equipments) < 2:
            print("需要至少两件装备才能比较")
            return
        print("选择第一件装备:")
        equip1 = select_item_from_list(equipments)
        if not equip1:
            return
        clear_screen()
        print("选择第二件装备:")
        equip2 = select_item_from_list(equipments)
        if not equip2:
            return
        clear_screen()
        print(equip1.compare_with(equip2))
