from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box

from inventory.equipment import Equipment

class Inventory:
    def __init__(self) -> None:
        self.items = []

    @property
    def total_worth(self):
        return sum(item.amount * item.individual_value for item in self.items)

    def get_total_item_count(self) -> int:
        return sum(item.amount for item in self.items)

    def get_items_by_type(self, item_type):
        """按物品类型获取物品列表"""
        return [item for item in self.items if item.object_type == item_type]

    def get_items_by_class(self, cls):
        """按物品类获取物品列表"""
        return [item for item in self.items if isinstance(item, cls)]

    def add_item(self, item):
        item.add_to_inventory(self, item.amount)

    def remove_item(self, item, amount=1):
        for i, inventory_item in enumerate(self.items):
            if inventory_item.name == item.name:
                inventory_item.amount -= amount
                if inventory_item.amount <= 0:
                    self.items.pop(i)
                return True
        return False

    def get_item_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def decrease_item_amount(self, item, amount):
        for actual_item in self.items:
            if item.name == actual_item.name:
                actual_item.amount -= amount
                if actual_item.amount <= 0:
                    self.items.remove(actual_item)
                return True
        return False

    def get_equipments(self):
        return self.get_items_by_class(Equipment)

    def get_consumables(self):
        return self.get_items_by_type("consumable")

    def get_formatted_inventory_table(self):
        """返回格式化的库存表格"""
        if not self.items:
            return Text("背包是空的", style="dim")
    
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE_HEAVY,
        )
    
        table.add_column("编号", justify="center", style="cyan", no_wrap=True)
        table.add_column("名称", style="bold cyan")
        table.add_column("类型", style="green")
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
