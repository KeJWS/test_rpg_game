import combat
import random
import text, shops, items, enemies, quest

# 处理事件（遭遇敌人、商店、治疗场所......）
class Event():
    def __init__(self, name, success_chance, is_unique) -> None:
        self.name = name
        self.success_chance = success_chance
        self.is_unique = is_unique

    def check_success(self):
        if self.success_chance < random.randint(0, 100):
            return False
        return True

    def add_event_to_event_list(self):
        if type(self) == Fixed_combat_event:
            event_type_list[0].append(self)
        elif type(self) == Shop_event:
            event_type_list[1].append(self)
        elif type(self) == Healing_event:
            event_type_list[2].append(self)

class Random_combat_event(Event):
    def __init__(self, name) -> None:
        super().__init__(name, 100, False)
        self.enemy_quantity_for_level = {
            2: 1,
            5: 2,
            7: 3,
            13: 4,
            100: 5,
        }

    def effect(self, player):
        enemy_group = combat.create_enemy_group(player.level, enemies.possible_enemies, self.enemy_quantity_for_level)
        combat.combat(player, enemy_group)

class Fixed_combat_event(Event):
    def __init__(self, name, enemy_list) -> None:
        super().__init__(name, 10, True)
        self.enemy_list = enemy_list

    def effect(self, player):
        combat.combat(player, self.enemy_list)

class Shop_event(Event):
    def __init__(self, name, is_unique, encounter_text, enter_text, talk_text, exit_text, item_set, quest) -> None:
        super().__init__(name, 100, is_unique)
        self.encounter = encounter_text
        self.enter = enter_text
        self.exit = exit_text
        self.talk = talk_text
        self.item_set = item_set
        self.quest = quest

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
                    if self.quest != None and self.quest.status == "Not Active":
                        self.quest.propose_quest(player)
                    else:
                        print(self.talk)
                text.shop_menu(player)
                option = input("> ").lower()
        print(self.exit)

class Healing_event(Event):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, success_chance, is_unique, healing_amount) -> None:
        super().__init__(name, success_chance, is_unique)
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

class Inn_event(Healing_event):
    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, healing_amount, cost) -> None:
        super().__init__(name, encounter_text, success_text, fail_text, refuse_text, 100, False, healing_amount)
        self.cost = cost

    def effect(self, player):
        print(self.encounter)
        accept = input("> ").lower()
        while accept not in ["y", "n"]:
            accept == input("> ").lower()
        if accept == "y":
            if player.money >= self.cost:
                print(self.success)
                player.heal(self.healing_amount)
                player.money -= self.cost
            else:
                print(self.fail)
        elif accept == "n":
            print(self.refuse)

### 生命恢复水晶 ###
def life_recovery_crystal(my_player):
    cost = 50 * my_player.level
    print("\n" + "="*34)
    print(f"一个神秘的魔法水晶, 可以完全恢复,\n但需要花费: {cost}G")
    print("-"*34)
    if my_player.money < cost:
        print("金币不足!")
        return
    if input("确认抚摸吗? (y/n): ").lower() == 'y':
        my_player.money -= cost
        combat.fully_heal(my_player)
        combat.fully_recover_mp(my_player)
    else:
        print("已取消。")

# 任务
# -> 凯撒鲁斯
caesarus_bandit_combat = Fixed_combat_event('凯撒鲁斯与他的强盗', enemies.enemy_list_caesarus_bandit)
quest_caesarus_bandit = quest.Quest('凯撒鲁斯与他的强盗', text.quest_caesarus_bandit_text, text.shop_quest_caesarus_bandits, 150, 150, None, caesarus_bandit_combat, 5)

# 事件实例
random_combat = Random_combat_event("随机战斗")
shop_rik_armor = Shop_event("里克的盔甲店", False, text.rik_armor_shop_encounter, text.rik_armor_shop_enter, text.rik_armor_shop_talk, text.rik_armor_shop_exit, items.rik_armor_shop_item_set, quest_caesarus_bandit)
shop_itz_magic = Shop_event("伊兹的魔法店", False, text.itz_magic_encounter, text.itz_magic_enter, text.itz_magic_talk, text.itz_magic_exit, items.itz_magic_item_set, None)
heal_medussa_statue = Healing_event("美杜莎雕像", text.medussa_statue_encounter, text.medussa_statue_success,
                                    text.medussa_statue_fail, text.medussa_statue_refuse, 70, False, 90)
inn_event = Inn_event("Inn", text.inn_event_encounter, text.inn_event_success, text.inn_event_fail, text.inn_event_refuse, 120, 20)

# 事件分类
combat_event_list = [random_combat]
shop_event_list = [shop_itz_magic, shop_rik_armor]
heal_event_list = [heal_medussa_statue, inn_event]

# 按类型分类的事件列表
event_type_list = [combat_event_list, shop_event_list, heal_event_list]
