import test.fx as fx
from test.clear_screen import clear_screen
import inventory.utils as utils
from inventory.equipment import Equipment

class Inventory_interface:
    def __init__(self, inventory):
        self.inventory = inventory

    def show_inventory(self):
        print(f"{fx.BOLD_UNDERLINED}背包内容:{fx.END}")
        print(self.inventory.get_formatted_inventory_table())

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
        return utils.select_item_from_list(equipments, "装备什么?")

    def use_item(self):
        consumables = self.inventory.get_consumables()
        if not consumables:
            print("背包中没有可使用的物品")
            return None
        item = utils.select_item_from_list(consumables, "使用什么?")
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
        equip1 = utils.select_item_from_list(equipments)
        if not equip1:
            return
        clear_screen()
        print("选择第二件装备:")
        equip2 = utils.select_item_from_list(equipments)
        if not equip2:
            return
        clear_screen()
        print(equip1.compare_with(equip2))

    def upgrade_equipment(self):
        equipments = self.inventory.get_equipments()
        if not equipments:
            print("没有可强化的装备")
            return
        equipment = utils.select_item_from_list(equipments, "选择要强化的装备:")
        if equipment:
            equipment.upgrade()

    def repair_equipment(self):
        equipments = [eq for eq in self.inventory.get_equipments() if eq.durability < eq.max_durability]
        if not equipments:
            print("没有需要修理的装备")
            return
        equipment = utils.select_item_from_list(equipments, "选择要修理的装备:")
        if equipment:
            print(f"修理 {equipment.name} (当前耐久: {equipment.durability}/{equipment.max_durability})")
            print("1. 完全修理\n2. 部分修理\n0. 取消")
            choice = input("> ")
            if choice == "1":
                equipment.repair()
            elif choice == "2":
                try:
                    amount = int(input(f"修理多少点? (最多 {equipment.max_durability - equipment.durability}): "))
                    if 0 < amount <= (equipment.max_durability - equipment.durability):
                        equipment.repair(amount)
                    else:
                        print("无效的数量")
                except ValueError:
                    print("请输入有效数字")
