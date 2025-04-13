import sys
sys.path.append("..")
import items

def give_initial_items(my_player):
    option = str(input("> "))
    while option not in ["1", "2", "3"]:
        option = str(input("> "))
    if option == "1":
        items.rusty_sword.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
        items.atk_jewel.add_to_inventory_player(my_player.inventory)
    elif option == "2":
        items.broken_dagger.add_to_inventory_player(my_player.inventory)
        items.novice_armor.add_to_inventory_player(my_player.inventory)
        items.agi_jewel.add_to_inventory_player(my_player.inventory)
    elif option == "3":
        items.old_staff.add_to_inventory_player(my_player.inventory)
        items.old_robes.add_to_inventory_player(my_player.inventory)
        items.grimoire_fireball.add_to_inventory_player(my_player.inventory)

    items.mp_potion.add_to_inventory_player(my_player.inventory)
    items.hp_potion.add_to_inventory_player(my_player.inventory)
    my_player.add_money(100)
