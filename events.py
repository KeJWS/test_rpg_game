"""
事件系统模块，定义游戏中各类可能发生的事件及其处理逻辑。

该模块实现了游戏中的各种事件类型，包括战斗事件、商店事件、
治疗事件、伤害事件、宝箱事件等。每种事件都有自己的特定效果
和触发条件，丰富了游戏的探索体验和互动元素。
"""

import random
from typing import List, Callable

import combat
import data.items_data as items_data
import enemies
import ui.text as text
import data.event_text as event_text
from core import shops
from inventory import Inventory_interface as interface
from ui.clear_screen import enter_clear_screen, clear_screen

def ask_yes_no(prompt="> "):
    """
    获取用户的是/否输入。

    反复提示用户输入，直到获得有效的y或n响应。

    参数:
        prompt: 显示给用户的提示字符串

    返回:
        bool: 用户输入为y时返回True，为n时返回False
    """
    ans = input(prompt).strip().lower()
    while ans not in ["y", "n"]:
        ans = input(prompt).strip().lower()
    return ans == "y"

class Event():
    """
    事件基类，所有具体事件类型的父类。

    定义了事件的基本属性和检查事件是否成功的方法，
    具体的事件效果由子类实现。
    """

    def __init__(self, name, success_chance, is_unique) -> None:
        """
        初始化事件基本属性。

        参数:
            name: 事件名称
            success_chance: 事件成功的概率（0-100）
            is_unique: 事件是否为唯一事件（只能触发一次）
        """
        self.name = name
        self.success_chance = success_chance
        self.is_unique = is_unique

    def check_success(self):
        """
        检查事件是否成功触发。

        基于事件的成功概率和随机数生成来确定。

        返回:
            bool: 事件成功时返回True，否则返回False
        """
        return self.success_chance >= random.randint(0, 100)

class RandomCombatEvent(Event):
    """
    随机战斗事件类，用于生成基于玩家等级的随机战斗。

    根据玩家等级和预设的敌人数量规则生成适合的敌人组合。
    """

    def __init__(self, name) -> None:
        """
        初始化随机战斗事件。

        设置事件名称并定义不同玩家等级对应的最大敌人数量。

        参数:
            name: 事件名称
        """
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
        """
        触发随机战斗事件的效果。

        根据玩家等级创建敌人组合并开始战斗。

        参数:
            player: 当前玩家对象
        """
        enemy_group = enemies.create_enemy_group(player.ls.level, enemies.possible_enemies, self.enemy_quantity_for_level)
        combat.combat(player, enemy_group)

class FixedCombatEvent(Event):
    """
    固定战斗事件类，用于预设的特定敌人组合战斗。

    通常用于BOSS战或任务关卡，具有固定的敌人组合。
    """

    def __init__(self, name, enemy_list: List) -> None:
        """
        初始化固定战斗事件。

        参数:
            name: 事件名称
            enemy_list: 预设的敌人列表
        """
        super().__init__(name, 100, True)
        self.enemy_list = enemy_list

    def effect(self, player):
        """
        触发固定战斗事件的效果。

        使用预设的敌人列表开始战斗。

        参数:
            player: 当前玩家对象

        返回:
            bool: 战斗结果，True表示玩家逃跑，False表示战斗结束
        """
        return combat.combat(player, self.enemy_list)

class ShopEvent(Event):
    """
    商店事件类，用于表示游戏中的商店交互。

    玩家可以在商店中购买物品、出售物品、与商人交谈等。
    """

    def __init__(self, name, is_unique, encounter_text, enter_text, talk_text, exit_text, item_set):
        """
        初始化商店事件。

        参数:
            name: 商店名称
            is_unique: 商店是否为唯一事件
            encounter_text: 遇到商店时的描述文本
            enter_text: 进入商店时的描述文本
            talk_text: 与商人交谈时的描述文本
            exit_text: 离开商店时的描述文本
            item_set: 商店出售的物品集合
        """
        super().__init__(name, 100, is_unique)
        self.encounter, self.enter, self.talk, self.exit, self.item_set = encounter_text, enter_text, talk_text, exit_text, item_set

    def effect(self, player):
        """
        触发商店事件的效果。

        显示商店界面，允许玩家进行各种商店操作，如购买、
        出售物品、与商人交谈等。

        参数:
            player: 当前玩家对象
        """
        print(self.encounter)
        if ask_yes_no():
            print(self.enter)
            vendor = shops.Shop(self.item_set)
            while True:
                text.shop_menu(player)
                option = input("> ").lower()
                if option == "q":
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
    """
    治疗事件类，表示可以恢复玩家生命值的场所或物品。

    玩家可以选择使用治疗源，有一定概率成功恢复生命值。
    """

    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, success_chance, is_unique, healing_amount):
        """
        初始化治疗事件。

        参数:
            name: 事件名称
            encounter_text: 遇到治疗源时的描述文本
            success_text: 治疗成功时的描述文本
            fail_text: 治疗失败时的描述文本
            refuse_text: 拒绝治疗时的描述文本
            success_chance: 治疗成功的概率（0-100）
            is_unique: 事件是否为唯一事件
            healing_amount: 恢复的生命值数量
        """
        super().__init__(name, success_chance, is_unique)
        self.encounter, self.success, self.fail, self.refuse = encounter_text, success_text, fail_text, refuse_text
        self.healing_amount = healing_amount

    def effect(self, player):
        """
        触发治疗事件的效果。

        询问玩家是否使用治疗源，如果同意则根据成功概率
        决定是否恢复生命值。

        参数:
            player: 当前玩家对象
        """
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
    """
    伤害事件类，表示可能对玩家造成伤害的危险情况。

    玩家可以尝试避开危险，有一定概率成功避免伤害。
    """

    def __init__(self, name, encounter_text, success_text, fail_text, success_chance, damage_amount):
        """
        初始化伤害事件。

        参数:
            name: 事件名称
            encounter_text: 遇到危险时的描述文本
            success_text: 成功避开危险时的描述文本
            fail_text: 遭受伤害时的描述文本
            success_chance: 成功避开危险的概率（0-100）
            damage_amount: 失败时受到的伤害值
        """
        super().__init__(name, success_chance, False)
        self.encounter, self.success, self.fail = encounter_text, success_text, fail_text
        self.damage_amount = damage_amount

    def effect(self, player):
        """
        触发伤害事件的效果。

        询问玩家是否尝试避开危险，结合成功概率决定
        玩家是否受到伤害。

        参数:
            player: 当前玩家对象
        """
        print(self.encounter)
        if ask_yes_no() and self.check_success():
            print(self.success)
        else:
            print(self.fail)
            player.take_dmg(self.damage_amount)

class InnEvent(HealingEvent):
    """
    旅店事件类，继承自治疗事件。

    玩家可以通过支付金币在旅店休息恢复生命值。
    """

    def __init__(self, name, encounter_text, success_text, fail_text, refuse_text, healing_amount, cost) -> None:
        """
        初始化旅店事件。

        参数:
            name: 旅店名称
            encounter_text: 遇到旅店时的描述文本
            success_text: 成功休息时的描述文本
            fail_text: 金币不足时的描述文本
            refuse_text: 拒绝入住时的描述文本
            healing_amount: 休息恢复的生命值
            cost: 入住旅店的金币花费
        """
        super().__init__(name, encounter_text, success_text, fail_text, refuse_text, 100, False, healing_amount)
        self.cost = cost

    def effect(self, player):
        """
        触发旅店事件的效果。

        询问玩家是否入住旅店，检查金币是否足够，
        如果条件满足则恢复生命值并扣除金币。

        参数:
            player: 当前玩家对象
        """
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
    """
    隐藏宝箱事件类，表示玩家可以发现并尝试打开的宝箱。

    成功打开宝箱可以获得奖励，失败则会触发陷阱造成伤害并引发战斗。
    """

    def __init__(self, name, item_name) -> None:
        """
        初始化隐藏宝箱事件。

        参数:
            name: 事件名称
            item_name: 宝箱中物品的名称ID
        """
        super().__init__(name, 100, False)
        self.item_name = item_name

    def effect(self, player):
        """
        触发隐藏宝箱事件的效果。

        询问玩家是否尝试开启宝箱，根据玩家属性计算成功率。
        成功则获得金币、经验和物品；失败则受到伤害并触发战斗。

        参数:
            player: 当前玩家对象
        """
        print("你发现了一个隐藏的宝箱，尝试开锁? [y/n]")
        if not ask_yes_no():
            print("你决定不去动这个宝箱")
            return
        lock_chance = player.stats["luk"] * 2 + player.stats["agi"] * 1.25 + player.ls.level
        if random.randint(0, 200) < min(lock_chance, 125):
            gold = random.randint(12, 35) + player.ls.level
            exp = random.randint(5, 25) * player.ls.level
            item = items_data.equipment_data[self.item_name]
            print(f"你成功打开了宝箱, 获得了不少好东西")
            player.add_money(gold)
            player.add_exp(exp)
            item.add_to_inventory_player(player.inventory)
        else:
            damage = int(player.stats["max_hp"] * 0.2)
            print("你触发了陷阱, 遭受伤害并引来了敌人!")
            player.take_dmg(damage)
            enemy_group = enemies.create_enemy_group(player.ls.level, enemies.possible_enemies, {100: 4})
            combat.combat(player, enemy_group)

class SimpleEvent(Event):
    """
    简单事件类，用于创建基于函数的轻量级事件。

    通过传入效果函数来定义事件行为，适合实现简单的奖励或文本事件。
    """

    def __init__(self, name, effect_func: Callable):
        """
        初始化简单事件。

        参数:
            name: 事件名称
            effect_func: 事件效果函数，接受player参数
        """
        super().__init__(name, 100, False)
        self._effect_func = effect_func

    def effect(self, player):
        """
        触发简单事件的效果。

        调用预设的效果函数并传入玩家对象。

        参数:
            player: 当前玩家对象
        """
        self._effect_func(player)

def find_coins(player):
    """
    发现金币事件处理函数。

    玩家发现少量金币，金额基于玩家等级。

    参数:
        player: 当前玩家对象
    """
    gold = random.randint(1, 5) * player.ls.level
    print(event_text.find_coins_text)
    player.add_money(gold)

def admire_scenery(player):
    """
    欣赏风景事件处理函数。

    玩家欣赏环境风景，获得少量经验值。

    参数:
        player: 当前玩家对象
    """
    exp = random.randint(5, 15) + player.ls.level
    print(event_text.admire_scenery_text)
    player.add_exp(exp)

def friendly_villager(player):
    """
    友好村民事件处理函数。

    遇到友好的村民，获得少量金币和生命恢复。

    参数:
        player: 当前玩家对象
    """
    gold = random.randint(5, 10)
    healing = int(player.stats["max_hp"] * 0.1)
    print(event_text.friendly_villager_text)
    player.add_money(gold)
    player.heal(healing)

def find_herb(player):
    """
    发现草药事件处理函数。

    玩家发现治疗草药，恢复一定量的生命值。

    参数:
        player: 当前玩家对象
    """
    healing = int(player.stats["max_hp"] * 0.2)
    print(event_text.find_herb_text)
    player.heal(healing)

def rest_spot(player):
    """
    休息地点事件处理函数。

    玩家发现安全的休息处，恢复较多生命值。

    参数:
        player: 当前玩家对象
    """
    healing = int(player.stats["max_hp"] * 0.3)
    print(event_text.rest_spot_text)
    player.heal(healing)
