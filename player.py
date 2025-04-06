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
        self.xp_to_next_level = 50
        self.aptitudes = {
            "str": 5,
            "dex": 5,
            "int": 5,
            "wis": 5,
            "const": 5
        }
        self.aptitude_points = 5
        self.auto_mode = False
        self.inventory = inventory.Inventory()
        self.equipment = {
            "weapon": None,
            "Armor": None
        }
        self.money = 0
        self.combos = []
        self.spells = [skills.fire_ball, skills.divineBlessing, skills.benettFantasticVoyage]

    def equip_item(self, equipment):
        if equipment is None:
            print("无法装备: 无效物品")
            return
        if not isinstance(equipment, inventory.Equipment):
            print(f"{equipment.name} 无法装备")
            return
        equip_type = equipment.equipment_type
        current_equipment = self.equipment.get(equip_type)
        # 卸下旧装备
        if current_equipment:
            current_equipment.add_to_inventory(self.inventory)
            for stat, value in current_equipment.stat_change_list.items():
                self.stats[stat] -= value
                print(f"{stat} -{value}")
        # 装备新装备
        self.equipment[equip_type] = equipment
        print(f"装备了 {equipment.name}")
        for stat, value in equipment.stat_change_list.items():
            self.stats[stat] += value
            print(f"{stat} +{value}")
        text.inventory_menu()
        self.inventory.show_inventory()

    def add_exp(self, exp):
        exp_value = (exp + self.stats["luk"]) * EXPERIENCE_RATE
        self.xp += exp_value
        print(f"获得了 {exp_value}xp")
        while(self.xp >= self.xp_to_next_level):
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = round(self.xp_to_next_level * 1.5)
            for stat in self.stats:
                self.stats[stat] += 1
            self.aptitude_points +=1
            combat.fully_heal(self)
            print(f"\033[33m升级！您现在的等级是: {self.level}\033[0m")

    def assign_aptitude_points(self):
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

    def update_stats_to_aptitudes(self, aptitude):
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
