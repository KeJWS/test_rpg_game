import random

import test.fx as fx
from inventory.item import Item

class Equipment(Item):
    def __init__(self, name, description, amount, individual_value, object_type, stat_change_list, combo, ascii_art):
        super().__init__(name, description, amount, individual_value, object_type)
        self.base_stats = stat_change_list.copy()
        self.stat_change_list = stat_change_list
        self.combo = combo
        self.durability = 100  # 耐久度
        self.max_durability = 100
        self.level = 0
        self.ascii_art = ascii_art or ""

    def show_ascii_art(self):
        return self.ascii_art

    def show_info(self):
        combo_name = fx.yellow(self.combo.name) if self.combo else ""
        return (
            f"[x{self.amount}] {self.name} ({self.object_type}) {self.show_stats()} - {self.individual_value}G {combo_name}\n"
            f"    简介: {self.description}"
        )

    def show_stats(self):
        stats_string = "[ "
        for stat in self.stat_change_list:
            sign = "+"
            if self.stat_change_list[stat] < 0:
                sign = ""
            stats_string += f"{stat} {sign}{self.stat_change_list[stat]} "
        stats_string += "]"
        return fx.green(stats_string)

    def get_detailed_info(self):
        info = super().get_detailed_info()
        ascii_art = self.show_ascii_art()
        info += fx.cyan(f"{ascii_art}\n")
        info += f"耐久: {self.durability}/{self.max_durability} [等级: +{self.level}]\n"
        info += "属性加成:\n"
        for stat, value in self.get_effective_stats().items():
            sign = "+" if value >= 0 else ""
            info += f"  {fx.GREEN}{stat}: {sign}{value}{fx.END}\n"
        return info

    def get_effective_stats(self):
        effective_stats = {}
        durability_factor = max(0.1, self.durability / self.max_durability)
        for stat, base in self.base_stats.items():
            upgrade_bonus = max(1, base * 0.2 * self.level)
            value = int((base + upgrade_bonus) * durability_factor)
            effective_stats[stat] = value
        return effective_stats

    def degrade_durability(self, amount: int = 1) -> bool:
        self.durability = max(0, self.durability - amount)
        if self.durability <= 0:
            print(f"{fx.RED}警告: {self.name} 已损坏，需要修理!{fx.END}")
            return False
        return True

    def repair(self, amount: int = None) -> None:
        if amount is None:
            self.durability = self.max_durability
            print(f"{self.name} 已完全修复")
        else:
            self.durability = min(self.durability + amount, self.max_durability)
            print(f"{self.name} 修复了 {amount} 点耐久度")

    def upgrade(self):
        print(f"尝试强化 {self.name}...")
        success_rate = max(100 - self.level * 15, 20)
        roll = random.randint(1, 100)

        if roll <= success_rate:
            self.level += 1
            print(f"强化成功! {self.name} 现在是 +{self.level} 等级")
            return True

        else:
            failure_type = random.randint(1, 20)
            if failure_type <= 15:
                degrade = random.randint(5, 15)
                self.degrade_durability(degrade)
                print(f"强化失败, 耐久度降低 {degrade}")
            elif failure_type <= 19:
                if self.level > 0:
                    self.level -= 1
                    print(f"{fx.RED}强化严重失败! {self.name} 降级到 +{self.level}{fx.END}")
                else:
                    degrade = random.randint(10, 25)
                    self.degrade_durability(degrade)
                    print(f"强化失败, 耐久度大幅降低 {degrade}")
            else:
                self.durability = 0
                print(f"{fx.RED}强化灾难性失败! {self.name} 已破碎，需要修理!{fx.END}")
            return False

    def compare_with(self, other_equipment):
        if not isinstance(other_equipment, Equipment):
            return "无法比较不同类型的物品"

        my_stats = self.get_effective_stats()
        other_stats = other_equipment.get_effective_stats()
        all_stats = set(list(my_stats.keys()) + list(other_stats.keys()))

        comparison = []
        for stat in all_stats:
            my_val = my_stats.get(stat, 0)
            other_val = other_stats.get(stat, 0)
            diff = my_val - other_val
            if diff > 0:
                comparison.append(f"{stat}: {my_val} +({diff})")
            elif diff < 0:
                comparison.append(f"{stat}: {my_val} +({diff})")
            else:
                comparison.append(f"{stat}: {my_val} (=)")

        return f"比较 {self.name} vs {other_equipment.name}:\n" + "\n".join(comparison)

    def clone(self, amount):
        new_eq = Equipment(self.name, self.description, amount, self.individual_value, self.object_type, self.base_stats.copy(), self.combo, self.ascii_art)
        new_eq.level = 0
        new_eq.durability = self.durability
        return new_eq
