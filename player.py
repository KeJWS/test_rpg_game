import  text, combat, inventory
from data.constants import EXPERIENCE_RATE, MONEY_MULTIPLIER

class Player(combat.Battler):
    def __init__(self, name) -> None:
        stats = {
            "max_hp": 1500,
            "hp": 500,
            "max_mp": 100,
            "mp": 100,
            "atk": 112,
            "def": 10,
            "mat": 12,
            "mdf": 10,
            "agi": 10,
            "luk": 10, # 幸运影响伤害, 经验获得量, 逃跑概率
            "crit": 3 # 影响暴击倍率
        }

        super().__init__(name, stats)

        self.level = 1 # 玩家等级
        self.xp = 0 # 当前经验值
        self.xp_to_next_level = self.exp_required_formula()
        self.aptitudes = {
            "str": 0,
            "dex": 0,
            "int": 0,
            "wis": 0,
            "const": 0
        }

        '''
        当能力提升时, 某些属性也会增加:
        STR -> ATK + 3
        DEX -> AGI + 2, CRIT + 1
        INT -> MAT + 3
        WIS -> MAXMP + 15
        CONST -> MAXHP + 30
        '''
        self.aptitude_points = 0 # 升级能力的点数
        self.inventory = inventory.Inventory() # 玩家的库存
        self.equipment = {      # 玩家的装备，可以进一步扩展
            "weapon": None,
            "shield": None, # 防御
            "head": None, # 防御
            "armor": None, # 防御和生命
            "hand": None, # 防御和攻击力
            "foot": None, # 防御和敏捷
            "accessory": None
        }
        self.money = 20 # 当前资金
        self.combos = [] # 玩家选择的组合（atk, cp）
        self.spells = [] # 玩家选择的法术（matk, mp）

        self.active_quests = []
        self.completed_quests = []

        self.is_ally = True # 检查战斗者是否是盟友

    def equip_item(self, equipment): # 装备一件物品（必须是“装备”类型）
        if isinstance(equipment, inventory.Equipment):
            actual_equipment = self.equipment[equipment.object_type]
            if actual_equipment != None:
                print(f"{actual_equipment.name} 已解除装备")
                actual_equipment.add_to_inventory(self.inventory, 1)
                if actual_equipment.combo != None:
                    self.combos.remove(actual_equipment.combo)
                    print(f"你不能再使用组合: {actual_equipment.combo.name}")
                for stat, value in actual_equipment.stat_change_list.items():
                    self.stats[stat] -= actual_equipment.stat_change_list[stat]
                    print(f"{stat} -{value}")
            for stat in equipment.stat_change_list:
                self.stats[stat] += equipment.stat_change_list[stat]
            self.equipment[equipment.object_type] = equipment.create_item(1)
            if equipment.combo != None and equipment.combo not in self.combos:
                self.combos.append(equipment.combo)
                print(f"您现在可以使用组合: {equipment.combo.name}")
            self.inventory.decrease_item_amount(equipment, 1)
            print(f"装备了 {equipment.name}")
            print(equipment.show_stats())
        else:
            if equipment != None:
                print(f"{equipment.name} 无法装备")
        text.inventory_menu()
        self.inventory.show_inventory()

    def use_item(self, item): # 使用物品
        usable_items = [inventory.Potion, inventory.Grimore]
        if item != None:
            if type(item) in usable_items:
                item.activate(self)
        text.inventory_menu()
        self.inventory.show_inventory()

    def add_exp(self, exp): # 为玩家增加一定数量的经验值
        exp_value = (exp + self.stats["luk"]) * EXPERIENCE_RATE
        self.xp += exp_value
        print(f"获得了 {exp_value}xp")
        # 升级:
        while(self.xp >= self.xp_to_next_level):
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self.exp_required_formula()
            for stat in self.stats:
                self.stats[stat] += 1
            self.stats["max_hp"] += 4
            self.stats["max_mp"] += 2
            self.aptitude_points +=1
            combat.fully_heal(self)
            combat.fully_recover_mp(self)
            print(f"\033[33m升级! 现在的等级是: {self.level}\033[0m, 有 {self.aptitude_points} 个能力点")

    def exp_required_formula(self):
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def add_money(self, money): # 给玩家添加一定数量的金钱
        self.money += money * MONEY_MULTIPLIER
        print(f"获得了 {money} 个硬币")

    def assign_aptitude_points(self): # 使用能力点数升级能力的循环
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

    def update_stats_to_aptitudes(self, aptitude): # 当能力提升时更新统计数据
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

    def show_quests(self):
        print("/// ACTIVE ///")
        for actq in self.active_quests:
            actq.show_info()
        print("/// COMPLETED ///")
        for cmpq in self.completed_quests:
            cmpq.show_info()
