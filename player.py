import  text, combat, inventory, skills
from test.constants import EXPERIENCE_RATE

class Player(combat.Battler):
    def __init__(self, name) -> None:
        stats = {
            "max_hp": 500,
            "hp": 500,
            "max_mp": 120,
            "mp": 120,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10, # 幸运影响伤害, 经验获得量, 逃跑概率
            "crit": 5
        }

        super().__init__(name, stats)

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50 # 达到下一等级所需的经验值每级乘以 1.5
        self.aptitudes = {
            "str": 5,
            "dex": 5,
            "int": 5,
            "wis": 5,
            "const": 5
        }
        self.aptitude_points = 0 # 升级能力的点数

        '''
        当能力提升时, 某些属性也会增加:
        STR -> ATK + 3
        DEX -> AGI + 3, CRIT + 1
        INT -> MAT + 3
        WIS -> MAXMP + 10
        CONST -> MAXHP + 10
        '''

        self.inventory = inventory.Inventory()
        self.equipment = {      #玩家的装备，可以进一步扩展
            "weapon": None,
            "armor": None
        }
        self.money = 0
        self.combos = [] # 玩家选择的组合（攻击）
        self.spells = [skills.fire_ball, skills.divineBlessing, skills.benettFantasticVoyage]
        self.is_ally = True

    def equip_item(self, equipment): # 装备一件物品（必须是“装备”类型）
        if not isinstance(equipment, inventory.Equipment):
            print(f"{equipment.name} 无法装备")
            return
        equip_type = equipment.object_type
        current_equipment = self.equipment.get(equip_type)
        # 卸下旧装备
        if current_equipment:
            print(f"{current_equipment.name} 已解除装备")
            current_equipment.add_to_inventory(self.inventory)
            for stat, value in current_equipment.stat_change_list.items():
                self.stats[stat] -= value
                print(f"{stat} -{value}")
        # 装备新装备
        for stat in equipment.stat_change_list:
            self.stats[stat] += equipment.stat_change_list[stat]
        self.equipment[equip_type] = equipment
        print(f"装备了 {equipment.name}")
        print(equipment.show_stats())
        text.inventory_menu()
        self.inventory.show_inventory()

    def use_item(self, item): # 使用物品
        if item != None:
            if isinstance(item, inventory.Potion):
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
            self.xp_to_next_level = round(self.xp_to_next_level * 1.5)
            for stat in self.stats:
                self.stats[stat] += 1
            self.aptitude_points +=1
            combat.fully_heal(self)
            combat.fully_recover_mp(self)
            print(f"\033[33m升级! 现在的等级是: {self.level}\033[0m, 有 {self.aptitude_points} 个能力点")

    def add_money(self, money): # 给玩家添加一定数量的金钱
        self.money += money
        print(f"获得了 {money} 个硬币")

    def assign_aptitude_points(self): # 使用能力点数升级能力的循环
        text.show_aptitudes(self)
        option = int(input("> "))
        options_dictionary = {
            1: "str",
            2: "dex",
            3: "int",
            4: "wis",
            5: "const"
        }
        while option != 0:
            if option in range(1, 6):
                if self.aptitude_points >= 1:
                    aptitude_to_assign = options_dictionary[option]
                    self.aptitudes[aptitude_to_assign] += 1
                    print(f"{aptitude_to_assign} 增加到了 {self.aptitudes[aptitude_to_assign]}")
                    self.update_stats_to_aptitudes(aptitude_to_assign)
                    self.aptitude_points -= 1
                else:
                    print("没有足够的能力点!")
            else:
                print("不是有效字符！")
            option = int(input("> "))

    def update_stats_to_aptitudes(self, aptitude): # 当能力提升时更新统计数据
        aptitude_mapping = {
            "str": {"atk": 3},
            "dex": {"agi": 3, "crit": 1},
            "int": {"mat": 3},
            "wis": {"max_mp": 10},
            "const": {"max_hp": 10}
        }
        updates = aptitude_mapping.get(aptitude, {})
        for stat, value in updates.items():
            self.stats[stat] += value
