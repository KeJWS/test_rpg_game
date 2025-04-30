import random
from typing import Dict, List, Callable, Any

import combat, items, enemies
import ui.text as text
import data.event_text as event_text
from extensions import shops
from inventory import Inventory_interface as interface
from test.clear_screen import enter_clear_screen, clear_screen

def ask_yes_no(prompt="> "):
    """简化的用户确认输入处理"""
    ans = input(prompt).strip().lower()
    while ans not in ["y", "n"]:
        ans = input(prompt).strip().lower()
    return ans == "y"

# 处理事件（遭遇敌人、商店、治疗场所......）
class Event():
    def __init__(self, name, success_chance, is_unique) -> None:
        self.name = name
        self.success_chance = success_chance
        self.is_unique = is_unique

    def check_success(self):
        return self.success_chance >= random.randint(0, 100)

class RandomCombatEvent(Event):
    def __init__(self, name) -> None:
        super().__init__(name, 100, False)
        self.enemy_quantity_for_level = {
            4: 1,
            7: 2,
            18: 3,
            37: 4,
            55: 5,
            120: 6,
        }

    def effect(self, player):
        enemy_group = enemies.create_enemy_group(player.level, enemies.possible_enemies, self.enemy_quantity_for_level)
        combat.combat(player, enemy_group)

class FixedCombatEvent(Event):
    def __init__(self, name, enemy_list: List) -> None:
        super().__init__(name, 100, True)
        self.enemy_list = enemy_list

    def effect(self, player):
        return combat.combat(player, self.enemy_list)

class ShopEvent(Event):
    def __init__(self, name, is_unique, encounter_text, enter_text, talk_text, exit_text, item_set):
        super().__init__(name, 100, is_unique)
        self.encounter, self.enter, self.talk, self.exit, self.item_set = encounter_text, enter_text, talk_text, exit_text, item_set

    def effect(self, player):
        print(self.encounter)
        if ask_yes_no():
            print(self.enter)
            vendor = shops.Shop(self.item_set)
            while True:
                text.shop_menu(player)
                option = input("> ").lower()
                if option == "e":
                    break
                clear_screen()
                match option:
                    case "b": player.buy_from_vendor(vendor)
                    case "s": player.money += interface(player.inventory).sell_item()
                    case "t": print(self.talk)
                    case "ua": player.unequip_all()
                    case "si": vendor.inventory.show_inventory_item(); enter_clear_screen()
        print(self.exit)

class HealingEvent(Event):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, success_chance, is_unique, healing_amount):
        super().__init__(name, success_chance, is_unique)
        self.encounter, self.success, self.fail, self.refuse = encounter_text, success_text, fail_text, refuse_text
        self.healing_amount = healing_amount

    def effect(self, player):
        print(self.encounter)
        if not ask_yes_no():
            print(self.refuse)
            return
        if self.check_success():
            print(self.success)
            player.heal(self.healing_amount)
        else:
            print(self.fail)

class DamageEvent(Event):
    def __init__(self, name, encounter_text, success_text, fail_text, success_chance, damage_amount):
        super().__init__(name, success_chance, False)
        self.encounter, self.success, self.fail = encounter_text, success_text, fail_text
        self.damage_amount = damage_amount

    def effect(self, player):
        print(self.encounter)
        if ask_yes_no() and self.check_success():
            print(self.success)
        else:
            print(self.fail)
            player.take_dmg(self.damage_amount)

class InnEvent(HealingEvent):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, healing_amount, cost) -> None:
        super().__init__(name, encounter_text, success_text, fail_text, refuse_text, 100, False, healing_amount)
        self.cost = cost

    def effect(self, player):
        print(self.encounter)
        if ask_yes_no():
            if player.money >= self.cost:
                print(self.success)
                player.heal(self.healing_amount)
                player.money -= self.cost
            else:
                print(self.fail)
        else:
            print(self.refuse)

class HiddenChestEvent(Event):
    def __init__(self, name, item_name) -> None:
        super().__init__(name, 100, False)
        self.item_name = item_name

    def effect(self, player):
        print("你发现了一个隐藏的宝箱，尝试开锁? [y/n]")
        if not ask_yes_no():
            print("你决定不去动这个宝箱")
            return
        lock_chance = player.stats["luk"] * 2 + player.stats["agi"] * 1.25 + player.level
        if random.randint(0, 200) < min(lock_chance, 125):
            gold = random.randint(12, 35) + player.level
            exp = random.randint(5, 25) * player.level
            item = items.equipment_data[self.item_name]
            print(f"你成功打开了宝箱, 获得了不少好东西")
            player.add_money(gold)
            player.add_exp(exp)
            item.add_to_inventory_player(player.inventory)
        else:
            damage = int(player.stats["max_hp"] * 0.2)
            print("你触发了陷阱, 遭受伤害并引来了敌人!")
            player.take_dmg(damage)
            enemy_group = enemies.create_enemy_group(player.level, enemies.possible_enemies, {100: 4})
            combat.combat(player, enemy_group)

# 轻事件
class SimpleEvent(Event):
    def __init__(self, name, effect_func: Callable):
        super().__init__(name, 100, False)
        self._effect_func = effect_func

    def effect(self, player):
        self._effect_func(player)

# 定义简化的轻事件
def find_coins(player):
    gold = random.randint(1, 5) * player.level
    print(event_text.find_coins_text)
    player.add_money(gold)

def admire_scenery(player):
    exp = random.randint(5, 15) + player.level
    print(event_text.admire_scenery_text)
    player.add_exp(exp)

def friendly_villager(player):
    gold = random.randint(5, 10)
    healing = int(player.stats["max_hp"] * 0.1)
    print(event_text.friendly_villager_text)
    player.add_money(gold)
    player.heal(healing)

def find_herb(player):
    healing = int(player.stats["max_hp"] * 0.2)
    print(event_text.find_herb_text)
    player.heal(healing)

def rest_spot(player):
    healing = int(player.stats["max_hp"] * 0.3)
    print(event_text.rest_spot_text)
    player.heal(healing)
