import inventory
import random

class Shop():
    def __init__(self, item_set) -> None:
        self.item_set = item_set
        self.inventory = inventory.Inventory()
        self.add_items_to_inventory_shop()

    def add_items_to_inventory_shop(self):
        item_quantity = random.randint(len(self.item_set), len(self.item_set) * 2)
        for _ in range(item_quantity):
            random.choice(self.item_set).add_to_inventory(self.inventory, 1)
