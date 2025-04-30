import random

import combat, items, enemies
import ui.text as text
import data.event_text as event_text
from extensions import shops
from inventory import Inventory_interface as interface
from test.clear_screen import enter_clear_screen, clear_screen

def ask_yes_no(prompt="> "):
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

class Random_combat_event(Event):
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

class Fixed_combat_event(Event):
    def __init__(self, name, enemy_list) -> None:
        super().__init__(name, 100, True)
        self.enemy_list = enemy_list

    def effect(self, player):
        escaped = combat.combat(player, self.enemy_list)
        return escaped

class Shop_event(Event):
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

class Healing_event(Event):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, success_chance, is_unique, healing_amount):
        super().__init__(name, success_chance, is_unique)
        self.encounter, self.success, self.fail, self.refuse = encounter_text, success_text, fail_text, refuse_text
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

class Damage_event(Event):
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

class Inn_event(Healing_event):
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
        accept = input("> ").lower()
        while accept not in ["y", "n"]:
            accept = input("> ").lower()

        if accept == "y":
            lock_chance = player.stats["luk"] * 2 + player.stats["agi"] * 1.25 + player.level
            if random.randint(0, 200) < min(lock_chance, 125):
                gold = random.randint(10, 20) + player.level * 2
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
        else:
            print("你决定不去动这个宝箱")

# 轻事件
class SimpleEvent(Event):
    def __init__(self, name, effect_func):
        super().__init__(name, 100, False)
        self._effect_func = effect_func

    def effect(self, player):
        self._effect_func(player)

# 定义简化的轻事件
def find_coins(player):
    gold = random.randint(1, 3) * player.level
    print(event_text.find_coins_text)
    player.add_money(gold)

def admire_scenery(player):
    exp = random.randint(5, 10) + player.level
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

### 生命恢复水晶 ###
def life_recovery_crystal(my_player):
    cost = 35 * my_player.level
    print("\n" + "="*34)
    print(f"一个神秘的魔法水晶, 可以完全恢复,\n但需要花费: {cost}G")
    print("-"*34)
    if my_player.money < cost:
        print("金币不足!")
        return
    if input("确认抚摸吗? (y/n): ").lower() == 'y':
        my_player.money -= cost
        my_player.recover_mp(9999); my_player.heal(9999)
    else:
        print("已取消。")

# 事件实例
random_combat = Random_combat_event("随机战斗")
shop_rik_armor = Shop_event("里克的盔甲店", False, event_text.rik_armor_shop_encounter, event_text.rik_armor_shop_enter, \
                            event_text.rik_armor_shop_talk, event_text.rik_armor_shop_exit, items.rik_armor_shop_item_set)
shop_itz_magic = Shop_event("伊兹的魔法店", False, event_text.itz_magic_encounter, event_text.itz_magic_enter, event_text.itz_magic_talk, \
                            event_text.itz_magic_exit, items.itz_magic_item_set)
heal_medussa_statue = Healing_event("美杜莎雕像", event_text.medussa_statue_encounter, event_text.medussa_statue_success,
                                    event_text.medussa_statue_fail, event_text.medussa_statue_refuse, 75, False, 90)
inn_event = Inn_event("客栈", event_text.inn_event_encounter, event_text.inn_event_success, event_text.inn_event_fail, event_text.inn_event_refuse, 150, 25)

shop_anna_armor = Shop_event("安娜的防具店", False, event_text.anna_armor_shop_encounter, event_text.anna_armor_shop_enter, \
                             event_text.anna_armor_shop_talk, event_text.anna_armor_shop_exit, items.anna_armor_shop_set)
shop_jack_weapon = Shop_event("杰克的武器店", False, event_text.jack_weapon_shop_encounter, event_text.jack_weapon_shop_enter, \
                              event_text.jack_weapon_shop_talk, event_text.jack_weapon_shop_exit, items.jack_weapon_shop_set)

shop_lok_armor = Shop_event("青铜匠武具店", False, event_text.lok_armor_shop_encounter, event_text.lok_armor_shop_enter, \
                            event_text.lok_armor_shop_talk, event_text.lok_armor_shop_exit, items.lok_armor_shop_item_set)
