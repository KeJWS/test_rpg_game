"""
库存系统模块，实现游戏中的物品管理功能。

该模块定义了库存系统的核心组件，提供物品的存储、检索、添加和移除等基本功能。
支持物品的分类统计、查找和排序，并提供格式化的库存显示。作为游戏中物品
管理的核心系统，连接了玩家与游戏世界的物品交互。
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box

from others.equipment import Equipment

console = Console()

class Inventory:
    """
    库存类，管理游戏中的物品收集和存储。

    提供物品的添加、移除、计数和检索等基本功能，同时支持物品分类和库存显示。
    作为玩家与游戏物品系统交互的核心接口，管理所有物品的生命周期。

    属性:
        items (list): 存储在库存中的物品列表
    """
    def __init__(self) -> None:
        """
        初始化一个空的库存实例。

        创建一个新的库存对象，初始化物品列表为空。
        """
        self.items = []

    @property
    def total_worth(self):
        """
        计算库存中所有物品的总价值。

        将每个物品的数量乘以单价，然后求和得到总价值。

        返回:
            int: 库存中所有物品的总价值
        """
        return sum(item.amount * item.individual_value for item in self.items)

    def get_total_item_count(self) -> int:
        """
        获取库存中所有物品的总数量。

        计算库存中所有物品数量的总和。

        返回:
            int: 库存中所有物品的总数量
        """
        return sum(item.amount for item in self.items)

    def get_items_by_type(self, item_type):
        """
        按物品类型获取物品列表。

        根据物品的object_type属性筛选并返回符合条件的物品列表。

        参数:
            item_type (str): 要筛选的物品类型

        返回:
            list: 符合指定类型的物品列表
        """
        return [item for item in self.items if item.object_type == item_type]

    def get_items_by_class(self, cls):
        """
        按物品类获取物品列表。

        根据物品的Python类型筛选并返回符合条件的物品列表。

        参数:
            cls (class): 要筛选的物品类

        返回:
            list: 符合指定类的物品列表
        """
        return [item for item in self.items if isinstance(item, cls)]

    def add_item(self, item):
        """
        向库存中添加物品。

        调用物品的add_to_inventory方法将其添加到当前库存中。

        参数:
            item: 要添加的物品对象

        副作用:
            - 如果库存中已有同名物品，增加其数量
            - 否则将新物品添加到库存列表
        """
        item.add_to_inventory(self, item.amount)

    def remove_item(self, item, amount=1):
        """
        从库存中移除指定数量的物品。

        根据物品名称查找并减少指定数量，如果数量减至0则从库存中移除该物品。

        参数:
            item: 要移除的物品对象
            amount (int, optional): 要移除的数量，默认为1

        返回:
            bool: 如果成功移除返回True，物品不存在返回False

        副作用:
            - 减少库存中对应物品的数量
            - 可能从库存列表中移除物品
        """
        for i, inventory_item in enumerate(self.items):
            if inventory_item.name == item.name:
                inventory_item.amount -= amount
                if inventory_item.amount <= 0:
                    self.items.pop(i)
                return True
        return False

    def remove_items_by_name(self, name: str, amount: int) -> bool:
        """
        尝试移除背包中指定名称的若干个物品。

        根据物品名称查找并减少指定数量，如果数量不足则不执行操作。

        参数:
            name (str): 要移除的物品名称
            amount (int): 要移除的数量

        返回:
            bool: 如果成功移除返回True，物品不存在或数量不足返回False

        副作用:
            - 减少库存中对应物品的数量
            - 可能从库存列表中移除物品
        """
        for item in self.items:
            if item.name == name:
                if item.amount >= amount:
                    item.amount -= amount
                    if item.amount == 0:
                        self.items.remove(item)
                    return True
        return False

    def count_item_by_name(self, name):
        """
        统计指定名称物品的数量。

        根据物品名称在库存中查找并返回其数量。

        参数:
            name (str): 要统计的物品名称

        返回:
            int: 物品的数量，如果不存在则返回0
        """
        for item in self.items:
            if item.name == name:
                return item.amount
        return 0

    def get_item_by_name(self, name):
        """
        根据名称获取物品对象。

        在库存中查找指定名称的物品并返回其对象。

        参数:
            name (str): 要查找的物品名称

        返回:
            object: 找到的物品对象，如果不存在则返回None
        """
        for item in self.items:
            if item.name == name:
                return item
        return None

    def decrease_item_amount(self, item, amount):
        """
        减少指定物品的数量。

        根据物品对象查找库存中对应的物品并减少其数量。

        参数:
            item: 要减少数量的物品对象
            amount (int): 要减少的数量

        返回:
            bool: 如果成功减少返回True，物品不存在返回False

        副作用:
            - 减少库存中对应物品的数量
            - 可能从库存列表中移除物品
        """
        for actual_item in self.items:
            if item.name == actual_item.name:
                actual_item.amount -= amount
                if actual_item.amount <= 0:
                    self.items.remove(actual_item)
                return True
        return False

    def get_equipments(self):
        """
        获取库存中所有装备类物品。

        使用get_items_by_class方法筛选出所有Equipment类型的物品。

        返回:
            list: 库存中所有装备物品的列表
        """
        return self.get_items_by_class(Equipment)

    def show_inventory_item(self):
        """
        显示库存中的所有物品。

        以编号和简要信息的形式显示库存中的每个物品。

        副作用:
            在控制台输出库存物品列表
        """
        for index, item in enumerate(self.items, start=1):
            console.print(f"{index} - {item.show_info()}")

    def sort_items(self):
        """
        整理背包物品，按类型和名称排序。

        对库存中的物品进行排序，首先按照物品的类名排序，然后按物品名称排序。

        返回:
            bool: 始终返回True表示排序完成

        副作用:
            - 重新排序库存中的物品列表
            - 在控制台输出提示信息
        """
        self.items.sort(key=lambda item: (type(item).__name__, item.name))
        print("背包已整理完成")
        return True

    def get_formatted_inventory_table(self):
        """
        返回格式化的库存表格。

        创建一个美观的表格显示库存中的物品，包括编号、名称、类型、数量和单价。
        如果库存为空，则返回一个显示"背包是空的"的面板。

        返回:
            tuple: 包含两个元素:
                - 显示物品的格式化面板
                - 显示物品总数和总价值的汇总文本

        副作用:
            无，仅生成文本显示对象
        """
        if not self.items:
            empty_panel = Panel.fit(Text("背包是空的", style="dim"), border_style="bold green")
            empty_summary = Text("物品总数: 0 | 总价值: 0G", style="dim")
            return empty_panel, empty_summary

        table = Table(
            show_header=True,
            header_style="bold white",
            box=box.SIMPLE_HEAVY,
        )

        table.add_column("编号", justify="center", no_wrap=True)
        table.add_column("名称", style="bold cyan")
        table.add_column("类型", style="cyan")
        table.add_column("数量", justify="right", style="white")
        table.add_column("单价", justify="right", style="yellow")

        for i, item in enumerate(self.items, 1):
            table.add_row(
                str(i),
                item.name,
                str(item.object_type),
                f"x{item.amount}",
                f"{item.individual_value}G"
            )

        summary_text = Text()
        summary_text.append(f"\n物品总数: ", style="bold white")
        summary_text.append(f"{self.get_total_item_count()}", style="bold green")
        summary_text.append(" | 总价值: ", style="bold white")
        summary_text.append(f"{self.total_worth}G", style="bold yellow")

        return Panel.fit(
            table,
            subtitle="['0' 关闭背包]",
            border_style="bold green"
        ), summary_text
