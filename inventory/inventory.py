from inventory import utils

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
        """返回格式化的库存表格字符串"""
        if not self.items:
            return "背包是空的"
        headers = ["编号", "名称", "类型", "数量", "单价"]
        data = []
        for i, item in enumerate(self.items, 1):
            data.append([
                i,
                item.name,
                str(item.object_type),
                f"x{item.amount}",
                f"{item.individual_value}G",
            ])

        table = utils.format_table(headers, data)
        summary = f"\n物品总数: {self.get_total_item_count()} | 总价值: {self.total_worth}G"
        return table + summary

    def show_inventory_item(self):
        for index, item in enumerate(self.items, start=1):
            print(f"{index} - {item.show_info()}")
