from rich.console import Console

import test.fx as fx
from test.clear_screen import clear_screen

console = Console()

def select_item_from_list(item_list, prompt="选择一个物品:", allow_exit=True):
    """显示项目列表并提示用户选择一个"""
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

class Inventory_interface:
    def __init__(self, inventory):
        self.inventory = inventory

    def show_inventory(self):
        print(f"{fx.BOLD_UNDERLINED}背包内容:{fx.END}")
        table_panel, summary_text = self.inventory.get_formatted_inventory_table()
        console.print(table_panel)
        console.print(summary_text)

    def drop_item(self):
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
        equipments = self.inventory.get_equipments()
        if not equipments:
            print("背包中没有可装备的物品")
            return None
        return select_item_from_list(equipments, "装备什么?")

    def use_item(self):
        consumables = self.inventory.get_consumables()
        if not consumables:
            print("背包中没有可使用的物品")
            return None
        item = select_item_from_list(consumables, "使用什么?")
        if item:
            self.inventory.decrease_item_amount(item, 1)
            return item
        return None

    def view_item(self):
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
