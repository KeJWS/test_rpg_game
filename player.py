import  text, combat, inventory
from data.constants import EXPERIENCE_RATE, MONEY_MULTIPLIER

import test.fx as fx

class Player(combat.Battler):
    '''
    玩家主类，负责处理所有与玩家属性和游戏进程相关的信息。

    Attributes:
    lvl: int
        玩家当前等级，默认为 1。
    xp: int
        玩家当前经验值 (XP)。
    xpToNextLvl: int
        升级所需的经验值。
    comboPoints: int
        当前连击点数 (CP)。
    aptitudes: Dictionary
        负责管理能力系统的字典。每种能力可提供以下属性加成：
            STR -> ATK + 3 （力量影响攻击）
            DEX -> SPD + 2, CRIT + 1 （敏捷影响速度和暴击率）
            INT -> MATK + 3 （智力影响魔法攻击）
            WIS -> MP + 15 （智慧影响魔法值）
            CONST -> MAXHP + 30 （体质影响最大生命值）
    aptitudePoints: int
        可用于提升能力的点数。
    inventory: Inventory
        玩家物品栏。
    equipment: Dictionary
        存储当前玩家装备的字典。
    money: int
        当前金钱（金币）。
    combos: List
        玩家可使用的连击列表。
    spells: List
        玩家可使用的法术列表。
    activeQuests: List
        当前进行中的任务列表。
    completedQuests: List
        已完成的任务列表。
    '''
    def __init__(self, name) -> None:
        stats = {
            "max_hp": 1500,
            "hp": 500,
            "max_mp": 100,
            "mp": 100,
            "atk": 12,
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

    def normal_attack(self, defender):
        self.add_combo_points(1)
        return super().normal_attack(defender)

    def equip_item(self, equipment):
        '''
        玩家装备指定物品，物品必须是“装备”类型。

        Parameters:
        equipment: Equipment
            需要装备的物品。
        '''
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
            self.equipment[equipment.object_type] = equipment.create_item(1)
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
        text.inventory_menu()
        self.inventory.show_inventory()

    def use_item(self, item):
        '''
        使用指定的物品。物品必须属于 "usable_items" 列表中的类型才能被使用。

        Parameters:
        item: Item
            要使用的物品。
        '''
        usable_items = [inventory.Potion, inventory.Grimore]
        if type(item) in usable_items:
            item.activate(self)
        text.inventory_menu()
        self.inventory.show_inventory()

    def add_exp(self, exp):
        '''
        增加玩家的经验值，并处理升级逻辑。
        升级时，玩家的生命值和魔法值将完全恢复，并且所有属性 +1。

        Parameters:
        exp: int
            要增加的经验值。
        '''
        exp_value = (exp + self.stats["luk"]) * EXPERIENCE_RATE
        self.xp += exp_value
        print(f"获得了 {fx.YELLO}{exp_value}xp{fx.END}")
        # 处理升级
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
            print(fx.yellow(f"升级! 现在的等级是: {self.level}, 有 {self.aptitude_points} 个能力点"))

    def exp_required_formula(self): # 经验需求计算公式，可调整
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def add_money(self, money):
        '''
        增加玩家的金钱。

        Parameters:
        money: int
            要增加的金币数量。
        '''
        self.money += money * MONEY_MULTIPLIER
        print(fx.yellow(f"获得了 {money*MONEY_MULTIPLIER} 枚硬币。(💰: {self.money})"))

    def assign_aptitude_points(self):
        '''
        能力点分配菜单。
        '''
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
        '''
        根据所提升的能力点分配对应的属性加成。

        Parameters:
        aptitude: str
            要升级的能力。
        '''
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
        '''
        从商店购买物品。

        Parameters:
        vendor: Shop
            玩家要购买物品的商店。
        '''
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
        '''
        显示当前任务，包括进行中的任务和已完成的任务。
        '''
        print("/// 进行中 ///")
        for actq in self.active_quests:
            actq.show_info()
        print("/// 已完成 ///")
        for cmpq in self.completed_quests:
            cmpq.show_info()

    def add_combo_points(self, points):
        '''
        增加一定数量的连击点数 (CP)。

        Parameters:
        points: int
            要增加的连击点数。
        '''
        self.combo_points += points
