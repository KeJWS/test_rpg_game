import combat
import random
import text, shops, items

# 处理事件（遭遇敌人、商店、治疗场所......）
class Event():
    def __init__(self, name, success_chance) -> None:
        self.name = name
        self.success_chance = success_chance

    def check_success(self):
        if self.success_chance < random.randint(0, 100):
            return False
        return True

class Random_combat_event(Event):
    def __init__(self, name) -> None:
        super().__init__(name, 100)

    def effect(self, player):
        enemies = combat.create_enemy_group(player.level)
        combat.combat(player, enemies)

class Shop_event(Event):
    def __init__(self, name, encounter_text, enter_text, talk_text, exit_text, item_set) -> None:
        super().__init__(name, 100)
        self.encounter = encounter_text
        self.enter = enter_text
        self.exit = exit_text
        self.talk = talk_text
        self.item_set = item_set

    def effect(self, player):
        print(self.encounter)
        enter = input("> ").lower()
        while enter not in ["y", "n"]:
            enter = input("> ").lower()
        if enter == "y":
            print(self.enter)
            vendor = shops.Shop(self.item_set)
            text.shop_menu(player)
            option = input("> ").lower()
            while option != "e":
                if option == "b":
                    player.buy_from_vendor(vendor)
                elif option == "s":
                    player.money += player.inventory.sell_item()
                elif option == "t":
                    print(self.talk)
                text.shop_menu(player)
                option = input("> ").lower()
        print(self.exit)

class Healing_event(Event):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, success_chance, healing_amount) -> None:
        super().__init__(name, success_chance)
        self.encounter = encounter_text
        self.success = success_text
        self.fail = fail_text
        self.refuse = refuse_text
        self.healing_amount = healing_amount

    def effect(self, player):
        print(self.encounter)
        accept = input(">").lower()
        while accept not in ["y", "n"]:
            accept = input("> ").lower()
        if accept == "y":
            if self.check_success():
                print(self.success)
                player.heal(self.healing_amount)
            else:
                print(self.fail)
        elif accept == "n":
            print(self.refuse)

# 事件实例
random_combat = Random_combat_event("随机战斗")
shop_rik_armor = Shop_event("里克的盔甲店", text.rik_armor_shop_encounter, text.rik_armor_shop_enter, text.rik_armor_shop_talk, text.rik_armor_shop_exit, items.rik_armor_shop_item_set)
shop_itz_magic = Shop_event("伊兹的魔法店", text.itz_magic_encounter, text.itz_magic_enter, text.itz_magic_talk, text.itz_magic_exit, items.itz_magic_item_set)
heal_medussa_statue = Healing_event("美杜莎雕像", text.medussa_statue_encounter, text.medussa_statue_success,
                                    text.medussa_statue_fail, text.medussa_statue_refuse, 70, 50)

# 分组事件
combat_event_list = [random_combat]
shop_event_list = [shop_itz_magic, shop_rik_armor]
heal_event_list = [heal_medussa_statue]

# 所有事件的列表，按类型划分
event_type_list = [combat_event_list, shop_event_list, heal_event_list]
