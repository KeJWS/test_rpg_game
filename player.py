from data.constants import EXPERIENCE_RATE, MONEY_MULTIPLIER
from rich.console import Console

import inventory
import ui.text as text
import test.fx as fx
from core import battler
from inventory.interface import Inventory_interface as interface
from test.clear_screen import clear_screen
import skills

console = Console()


class Player(battler.Battler):
    def __init__(self, name):
        stats = {
            "max_hp": 500, "hp": 500,
            "max_mp": 100, "mp": 100,
            "atk": 12, "def": 10, "mat": 12, "mdf": 10,
            "agi": 10, "luk": 10, "crit": 3, "anti_crit": 3
        }
        super().__init__(name, stats)

        self.level, self.xp = 1, 0
        self.xp_to_next_level = self.exp_required_formula()
        self.combo_points, self.aptitude_points = 0, 0
        self.aptitudes = {k: 0 for k in ("str", "dex", "int", "wis", "const")}
        self.inventory = inventory.Inventory() # 玩家的库存
        self.equipment = {
            "weapon": None,
            "shield": None,
            "head": None,
            "armor": None,
            "hand": None,
            "foot": None,
            "accessory": None
        }
        self.money = 0
        self.combos, self.spells = [], []
        self.active_quests, self.completed_quests = [], []
        self.class_name = ""
        self.is_ally = True
        self.auto_mode = False

    def normal_attack(self, defender, gain_cp=True):
        if gain_cp: self.add_combo_points(1)
        return super().normal_attack(defender)

    def equip_item(self, equipment):
        if not isinstance(equipment, inventory.Equipment):
            if equipment: print(f"{equipment.name} 无法装备")
            return

        current = self.equipment[equipment.object_type]
        if current:
            print(f"{current.name} 已解除装备")
            current.add_to_inventory(self.inventory, 1)
            if current.combo: self.combos.remove(current.combo); print(f"不能再使用组合: {current.combo.name}")
            if current.spell: self.spells.remove(current.spell); print(f"不能再使用技能: {current.spell.name}")
            for stat, value in current.stat_change_list.items():
                self.stats[stat] -= value; print(f"{stat} -{value}")

        for stat, value in equipment.stat_change_list.items():
            self.stats[stat] += value

        self.equipment[equipment.object_type] = equipment.clone(1)
        if equipment.combo and equipment.combo not in self.combos:
            self.combos.append(equipment.combo); print(f"现在可以使用组合: {equipment.combo.name}")
        if equipment.spell and equipment.spell not in self.spells:
            self.spells.append(equipment.spell); print(f"现在可以使用技能: {equipment.spell.name}")

        self.inventory.decrease_item_amount(equipment, 1)
        print(f"装备了 {equipment.name}\n{equipment.show_stats()}")

    def view_item_detail(self, item):
        clear_screen(); print(item.get_detailed_info()) if item else print("未选择任何物品")

    def unequip_all(self):
        for slot, eq in self.equipment.items():
            if not eq: continue
            print(f"- 已卸下 {eq.name}")
            for stat, value in eq.stat_change_list.items():
                self.stats[stat] -= value; print(fx.red(f"  {stat} -{value}"))
            if eq.combo in self.combos: self.combos.remove(eq.combo); print(f"  不再可用连招: {eq.combo.name}")
            if eq.spell in self.spells: self.spells.remove(eq.spell); print(f"  不再可用技能: {eq.spell.name}")
            self.inventory.add_item(eq)
            self.equipment[slot] = None
        print("所有装备已解除")

    def use_item(self, item):
        if type(item) in (inventory.Potion, inventory.Grimoire, inventory.Jewel):
            item.activate(self)

    def add_exp(self, exp):
        earned = (exp + self.stats["luk"]) * EXPERIENCE_RATE
        self.xp += earned
        console.print(f"获得了 {earned}xp")
        self.check_level_up()

    def check_level_up(self):
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self.exp_required_formula()
            self.handle_level_up()

    def handle_level_up(self):
        console.print(f"升级! 现在的等级是: {self.level}, 有 {self.aptitude_points + 1} 个能力点", style="bold yellow")
        self.aptitude_points += 1

        for stat in self.stats:
            self.stats[stat] += 1
        self.stats["crit"] -= 1
        self.stats["anti_crit"] -= 1
        self.stats["max_hp"] += 4
        self.stats["max_mp"] += 2

        self.apply_class_growth()
        self.recover_mp(9999)
        self.heal(9999)

    def apply_class_growth(self):
        growth = {
            "战士": {"atk": 2, "max_hp": 5},
            "盗贼": {"agi": 2, "crit": 1},
            "法师": {"mat": 2, "max_mp": 5},
            "弓箭手": {"atk": 2, "crit": 1},
            "圣骑士": {"atk": 2, "mat": 1, "max_hp": 10, "agi": -1},
            "死灵法师": {"mat": 3, "max_mp": 10, "max_hp": -15},
        }
        for stat, val in growth.get(self.class_name, {}).items():
            self.stats[stat] += val
            console.print(f"{stat} {'+' if val > 0 else ''}{val}", style="green" if val > 0 else "red")

    def exp_required_formula(self): # 经验需求计算公式
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def add_money(self, money):
        gained = money * MONEY_MULTIPLIER
        self.money += gained
        console.print(f"获得了 {gained} 枚硬币。(💰: {self.money})", style="yellow")

    def assign_aptitude_points(self):
        options = {"1": "str", "2": "dex", "3": "int", "4": "wis", "5": "const"}
        while True:
            text.show_aptitudes(self)
            option = input("> ").lower()
            if option == "q": break
            if self.aptitude_points <= 0:
                clear_screen(); print("没有足够的能力点!")
                continue
            if aptitude := options.get(option):
                self.aptitudes[aptitude] += 1
                clear_screen(); console.print(f"{aptitude} 增加到了 {self.aptitudes[aptitude]}")
                self.update_stats_to_aptitudes(aptitude)
                self.aptitude_points -= 1
            else:
                clear_screen(); print("请输入有效的数字")

    def update_stats_to_aptitudes(self, aptitude):
        mapping = {
            "str": {"atk": 3}, "dex": {"agi": 2, "crit": 1},
            "int": {"mat": 3}, "wis": {"max_mp": 15}, "const": {"max_hp": 30}
        }
        for stat, val in mapping.get(aptitude, {}).items():
            self.stats[stat] += val

    def buy_from_vendor(self, vendor):
        text.shop_buy(self)
        inv = interface(vendor.inventory)
        inv.show_inventory()
        while (choice := input("> ")) != "0":
            if choice.isdigit() and (idx := int(choice)) <= len(vendor.inventory.items):
                item = vendor.inventory.items[idx - 1]
                item.buy(self)
                if item.amount <= 0:
                    vendor.inventory.items.pop(idx - 1)
                inv.show_inventory()
            else:
                break

    def add_combo_points(self, points):
        self.combo_points += points

    def rebirth(self, world_map):
        print(fx.cyan("你选择了转生! 重置所有成长, 但保留了财富与物品"))
        self.unequip_all()
        saved_money, saved_inventory, saved_class = self.money, self.inventory, self.class_name
        self.__init__(self.name)
        self.money, self.inventory, self.class_name = saved_money, saved_inventory, saved_class
        self.active_quests.clear()
        self.completed_quests.clear()
        for region in world_map.regions.values():
            for q in region.quests:
                q.status = "Not Active"
        print(fx.cyan(f"你以 Lv.{self.level} 重生，保留了 {self.money} 金币和背包物品!"))
        interface(self.inventory).show_inventory()

    def change_auto_mode(self):
        self.auto_mode = not self.auto_mode
        print("-Auto mode-")
