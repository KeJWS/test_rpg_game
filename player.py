import  text, combat, inventory
from data.constants import EXPERIENCE_RATE, MONEY_MULTIPLIER

import test.fx as fx

class Player(combat.Battler):
    def __init__(self, name) -> None:
        self.class_name = ""
        stats = {
            "max_hp": 500,
            "hp": 500,
            "max_mp": 100,
            "mp": 100,
            "atk": 12,
            "def": 10,
            "mat": 12,
            "mdf": 10,
            "agi": 10,
            "luk": 10, # 幸运影响伤害, 经验获得量, 逃跑概率
            "crit": 3, # 影响暴击倍率
            "anti_crit": 5
        }

        super().__init__(name, stats)

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = self.exp_required_formula()
        self.combo_points = 0
        self.aptitudes = {
            "str": 0,
            "dex": 0,
            "int": 0,
            "wis": 0,
            "const": 0
        }
        self.aptitude_points = 0 # 升级能力的点数
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
        self.money = 20 # 当前资金
        self.combos = [] # 玩家选择的组合（atk, cp）
        # self.spells = []

        self.active_quests = []
        self.completed_quests = []

        self.is_ally = True # 检查战斗者是否是盟友

    def normal_attack(self, defender, gain_cp=True):
        if gain_cp:
            self.add_combo_points(1)
        return super().normal_attack(defender)

    def equip_item(self, equipment):
        if isinstance(equipment, inventory.Equipment):
            actual_equipment = self.equipment[equipment.object_type]
            if actual_equipment != None:
                print(f"{actual_equipment.name} 已解除装备")
                actual_equipment.add_to_inventory(self.inventory, 1)
                # 移除之前装备提供的连击
                if actual_equipment.combo != None:
                    self.combos.remove(actual_equipment.combo)
                    print(f"不能再使用组合: {actual_equipment.combo.name}")
                # 移除旧装备提供的属性加成
                for stat, value in actual_equipment.stat_change_list.items():
                    self.stats[stat] -= actual_equipment.stat_change_list[stat]
                    print(f"{stat} -{value}")
            # 增加新装备提供的属性加成
            for stat in equipment.stat_change_list:
                self.stats[stat] += equipment.stat_change_list[stat]
            self.equipment[equipment.object_type] = equipment.clone(1)
            # 添加新装备的连击
            if equipment.combo != None and equipment.combo not in self.combos:
                self.combos.append(equipment.combo)
                print(f"现在可以使用组合: {equipment.combo.name}")
            self.inventory.decrease_item_amount(equipment, 1)
            print(f"装备了 {equipment.name}")
            print(equipment.show_stats())
        else:
            if equipment != None:
                print(f"{equipment.name} 无法装备")

    def view_item_detail(self, item):
        if item:
            print("\n======= 物品详情 =======")
            print(item.get_detailed_info())
        else:
            print("未选择任何物品")

    def unequip_all(self):
        for slot, equipment in self.equipment.items():
            if equipment:
                print(f"- 已卸下 {equipment.name}")
                for stat, value in equipment.stat_change_list.items():
                    self.stats[stat] -= value
                    print(f"  {stat} -{value}")
                if equipment.combo and equipment.combo in self.combos:
                    self.combos.remove(equipment.combo)
                    print(f"  不再可用连招: {equipment.combo.name}")
                self.inventory.add_item(equipment)
                self.equipment[slot] = None
        print(f"所有装备已解除")

    def use_item(self, item):
        usable_items = [inventory.Potion, inventory.Grimoire, inventory.Jewel]
        if type(item) in usable_items:
            item.activate(self)

    def add_exp(self, exp):
        exp_value = (exp + self.stats["luk"]) * EXPERIENCE_RATE
        self.xp += exp_value
        print(f"获得了 {fx.YELLO}{exp_value}xp{fx.END}")
        # 处理升级
        while(self.xp >= self.xp_to_next_level):
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self.exp_required_formula()
            for stat in self.stats:
                self.stats[stat] += 2
            self.stats["crit"] -= 1
            self.stats["anti_crit"] -= 2
            self.stats["max_hp"] += 8
            self.stats["max_mp"] += 3
            self.aptitude_points +=1
            combat.fully_heal(self)
            combat.fully_recover_mp(self)
            print(fx.yellow(f"升级! 现在的等级是: {self.level}, 有 {self.aptitude_points} 个能力点"))

    def exp_required_formula(self): # 经验需求计算公式，可调整
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def add_money(self, money):
        self.money += money * MONEY_MULTIPLIER
        print(fx.yellow(f"获得了 {money*MONEY_MULTIPLIER} 枚硬币。(💰: {self.money})"))

    def assign_aptitude_points(self):
        options_dictionary = {
            "1": "str",
            "2": "dex",
            "3": "int",
            "4": "wis",
            "5": "const"
        }
        text.show_aptitudes(self)
        option = input("> ")
        while option.lower() != "q":
            try:
                if self.aptitude_points >= 1:
                    aptitude_to_assign = options_dictionary[option]
                    self.aptitudes[aptitude_to_assign] += 1
                    print(f"{aptitude_to_assign} 增加到了 {self.aptitudes[aptitude_to_assign]}")
                    self.update_stats_to_aptitudes(aptitude_to_assign)
                    self.aptitude_points -= 1
                else:
                    print("没有足够的能力点!")
            except:
                print("请输入有效的数字")
            option = input("> ")

    def update_stats_to_aptitudes(self, aptitude):
        aptitude_mapping = {
            "str": {"atk": 3},
            "dex": {"agi": 2, "crit": 1},
            "int": {"mat": 3},
            "wis": {"max_mp": 15},
            "const": {"max_hp": 30}
        }
        updates = aptitude_mapping.get(aptitude, {})
        for stat, value in updates.items():
            self.stats[stat] += value

    def buy_from_vendor(self, vendor):
        text.shop_buy(self)
        vendor.inventory.show_inventory()
        i = int(input("> "))
        while i != 0:
            if i <= len(vendor.inventory.items) and i > 0:
                vendor.inventory.items[i-1].buy(self)
                if vendor.inventory.items[i-1].amount <= 0:
                    vendor.inventory.items.pop(i-1)
                vendor.inventory.show_inventory()
                i = int(input("> "))

    def add_combo_points(self, points):
        self.combo_points += points

    def rebirth(self, world_map):
        print(fx.cyan("你选择了转生! 重置所有成长, 但保留了财富与物品"))
        self.unequip_all()

        saved_money = self.money
        saved_inventory = self.inventory
        saved_class_name = self.class_name
        # saved_spells = self.spells.copy()

        self.__init__(self.name)
        self.money = saved_money
        self.inventory = saved_inventory
        self.class_name = saved_class_name
        # self.spells = saved_spells

        self.active_quests.clear()
        self.completed_quests.clear()
    
        for region in world_map.regions.values():
            for q in region.quests:
                q.status = "Not Active"

        print(fx.cyan(f"你以 Lv.{self.level} 重生，保留了 {self.money} 金币和背包物品!"))
        self.inventory.show_inventory()
