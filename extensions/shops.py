import random
import sys
sys.path.append("..")
import inventory

class Shop():
    def __init__(self, item_set) -> None:
        self.item_set = item_set
        self.inventory = inventory.Inventory()
        self.add_items_to_inventory_shop()

    def add_items_to_inventory_shop(self):
        '''将新物品添加到商店的库存中'''
        item_quantity = random.randint(len(self.item_set)//2, len(self.item_set))
        for _ in range(item_quantity):
            base_item = random.choice(self.item_set)
            new_item = base_item.clone(1)
            if hasattr(new_item, "reroll_quality"):
                new_item.reroll_quality()
            new_item.add_to_inventory(self.inventory, 1)