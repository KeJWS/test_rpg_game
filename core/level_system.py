from data.constants import EXPERIENCE_RATE
from rich.console import Console

console = Console()

class LevelSystem:
    def __init__(self, level=1, xp=0, class_name=""):
        self.level = level
        self.xp = xp
        self.class_name = class_name
        self.aptitude_points = 0
        self.xp_to_next_level = self.exp_required_formula()

    def exp_required_formula(self):
        base = 100 * self.level
        growth = (self.level ** 2.5) * 1.25
        scaling = self.level * 35
        return round(base + growth + scaling)

    def gain_exp(self, battler, amount):
        earned = (amount + battler.stats["luk"]) * EXPERIENCE_RATE
        self.xp += earned
        console.print(f"获得了 {earned}xp")
        self.check_level_up(battler)

    def check_level_up(self, battler):
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self.exp_required_formula()
            self.level_up(battler)

    def level_up(self, battler):
        console.print(f"升级! 现在的等级是: {self.level}, 有 {self.aptitude_points + 1} 个能力点", style="bold yellow")
        self.aptitude_points += 1

        for stat in battler.stats:
            battler.stats[stat] += 1
        battler.stats["crit"] -= 1
        battler.stats["anti_crit"] -= 1
        battler.stats["max_hp"] += 4
        battler.stats["max_mp"] += 2

        self.apply_class_growth(battler)
        battler.recover_mp(9999)
        battler.heal(9999)

    def apply_class_growth(self, battler):
        growth = {
            "战士": {"atk": 2, "max_hp": 5},
            "盗贼": {"agi": 2, "crit": 1},
            "法师": {"mat": 2, "max_mp": 5},
            "弓箭手": {"atk": 2, "crit": 1},
            "圣骑士": {"atk": 2, "mat": 1, "max_hp": 10, "agi": -1},
            "死灵法师": {"mat": 3, "max_mp": 10, "max_hp": -15},
        }
        for stat, val in growth.get(self.class_name, {}).items():
            battler.stats[stat] += val
            console.print(f"{stat} {'+' if val > 0 else ''}{val}", style="green" if val > 0 else "red")
