"""
玩家模块，定义了玩家角色的基本属性和行为。

该模块包含Player类，继承自Battler基类，实现了玩家特有的功能，
包括装备管理、经验和金钱获取、能力点分配、饥饿系统以及转生机制等。
作为游戏核心组件，与战斗系统、物品系统和任务系统紧密交互。
"""

import random
from data.constants import MONEY_MULTIPLIER
from rich.console import Console

import inventory
import ui.text as text
import test.fx as fx
from skills import skills
from core import battler
from others.equipment import Equipment
from core.level_system import LevelSystem
from inventory.interface import Inventory_interface as interface
from test.clear_screen import clear_screen

console = Console()


class Player(battler.Battler):
    """
    玩家类，表示游戏中由用户控制的角色。

    继承自Battler基类，实现了玩家特有的属性和功能，如物品栏、装备系统、
    技能和连招系统、任务管理、饥饿机制等。玩家还具有等级系统和能力点
    分配功能，可以定制角色成长方向。

    属性:
        ls (LevelSystem): 等级系统，管理玩家等级、经验和升级机制
        combo_points (int): 连击点数，用于释放特殊技能
        aptitudes (dict): 玩家的能力倾向，影响各项属性成长
        inventory (Inventory): 玩家的物品栏，存储收集的物品
        equipment (dict): 玩家当前装备，分为武器、盾牌、头部等槽位
        money (int): 玩家拥有的金钱数量
        combos (list): 玩家可用的连招列表
        spells (list): 玩家可用的技能列表
        active_quests (list): 当前进行中的任务
        completed_quests (list): 已完成的任务
        is_ally (bool): 标识玩家是友方单位
        auto_mode (bool): 是否处于自动战斗模式
    """
    def __init__(self, name):
        """
        初始化玩家实例。

        设置玩家的基础属性，包括生命值、魔法值、攻击力、防御力等战斗属性，
        以及初始化物品栏、装备槽、任务列表等游戏系统。

        参数:
            name (str): 玩家角色名称
        """
        stats = {
            "max_hp": 500, "hp": 500,
            "max_mp": 100, "mp": 100,
            "max_hunger": 120, "hunger": 100,
            "atk": 12, "def": 10, "mat": 12, "mdf": 10,
            "agi": 10, "luk": 10, "crit": 3, "anti_crit": 3
        }
        super().__init__(name, stats)

        self.ls = LevelSystem()
        self.combo_points = 0
        self.aptitudes = {k: 0 for k in ("str", "dex", "int", "wis", "const")}
        self.inventory = inventory.Inventory()
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
        self.combos = []
        self.spells = []
        self.active_quests, self.completed_quests = [], []
        self.is_ally = True
        self.auto_mode = False

    def normal_attack(self, defender, gain_cp=True):
        """
        执行普通攻击。

        对目标单位执行基本攻击，同时可选择是否获得连击点数。

        参数:
            defender (Battler): 被攻击的目标
            gain_cp (bool): 是否获得连击点数，默认为True

        返回:
            int: 造成的伤害值
        """
        if gain_cp: self.combo_points += 1
        return super().normal_attack(defender)

    def equip_item(self, equipment):
        """
        装备物品。

        将指定装备放入对应的装备槽位，更新玩家属性，并处理移除旧装备的逻辑。
        装备可能提供属性加成、连招技能或法术能力。

        参数:
            equipment (Equipment): 要装备的物品

        副作用:
            - 更新玩家的装备槽位和属性值
            - 可能添加或移除连招和技能
            - 从物品栏移除装备的一个实例
            - 将移除的旧装备添加回物品栏
        """
        if not isinstance(equipment, Equipment):
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
        console.print(f"装备了 {equipment.name}\n{equipment.show_stats()}")

    def unequip_all(self):
        """
        卸下所有装备。

        将玩家所有装备槽中的装备移除，回收到物品栏中，
        同时移除所有装备提供的属性加成、连招和技能。

        副作用:
            - 清空所有装备槽
            - 移除所有装备提供的属性加成
            - 移除装备相关的连招和技能
            - 将所有装备添加回物品栏
        """
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

    def add_exp(self, exp):
        """
        增加玩家经验值。

        将指定经验值添加到玩家的等级系统中，可能触发升级。

        参数:
            exp (int): 要添加的经验值数量
        """
        self.ls.gain_exp(self, exp)

    def add_money(self, money):
        """
        增加玩家金钱。

        将指定金额加到玩家的金钱总数中，乘以金钱倍率后再计算。

        参数:
            money (int): 要添加的基础金钱数量
        """
        gained = money * MONEY_MULTIPLIER
        self.money += gained
        console.print(f"获得了 {gained} 枚硬币。(💰: {self.money})", style="yellow")

    def assign_aptitude_points(self):
        """
        分配能力点界面。

        显示玩家当前能力值并允许分配可用的能力点到不同能力上。
        每次分配会更新相关属性并消耗一个能力点。

        副作用:
            - 更新玩家的能力值
            - 根据分配的能力提升相应属性
            - 消耗等级系统中的能力点
        """
        options = {"1": "str", "2": "dex", "3": "int", "4": "wis", "5": "const"}
        while True:
            text.show_aptitudes(self)
            option = input("> ").lower()
            if option == "q": break
            if self.ls.aptitude_points <= 0:
                clear_screen(); print("没有足够的能力点!")
                continue
            if aptitude := options.get(option):
                self.aptitudes[aptitude] += 1
                clear_screen(); console.print(f"{aptitude} 增加到了 {self.aptitudes[aptitude]}")
                self.update_stats_to_aptitudes(aptitude)
                self.ls.aptitude_points -= 1
            else:
                clear_screen(); print("请输入有效的数字")

    def update_stats_to_aptitudes(self, aptitude):
        """
        根据能力值更新玩家属性。

        根据提升的能力类型，更新对应的玩家属性值。
        不同能力会影响不同的属性组合。

        参数:
            aptitude (str): 要更新的能力类型

        映射关系:
            - str(力量): 提升攻击力
            - dex(敏捷): 提升速度和暴击率
            - int(智力): 提升魔法攻击力
            - wis(智慧): 提升最大魔法值
            - const(体质): 提升最大生命值
        """
        mapping = {
            "str": {"atk": 3}, "dex": {"agi": 2, "crit": 1},
            "int": {"mat": 3}, "wis": {"max_mp": 15}, "const": {"max_hp": 30}
        }
        for stat, val in mapping.get(aptitude, {}).items():
            self.stats[stat] += val

    def buy_from_vendor(self, vendor):
        """
        从商人处购买物品。

        显示商人的物品列表，允许玩家选择并购买物品。
        购买成功会从玩家金钱中扣除相应费用并添加物品到背包。

        参数:
            vendor: 商人对象，包含可购买的物品列表
        """
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

    def decrease_hunger(self, amount):
        """
        减少玩家当前饱食度。

        降低玩家的当前饱食度值，可能触发饥饿警告或饥饿伤害。
        当饱食度低于20%时会发出警告，降至0时会造成随机伤害，
        可能导致玩家死亡。

        参数:
            amount (int): 要减少的饱食度值

        副作用:
            - 降低玩家当前饱食度
            - 可能显示饥饿警告
            - 饱食度为0时可能造成伤害
            - 极端情况可能导致玩家死亡
        """
        self.stats['hunger'] = max(0, self.stats['hunger'] - amount)
        if self.stats['hunger'] <= 20:
            console.print(f"警告: 饱食度过低 ({self.stats['hunger']}/{self.stats['max_hunger']})，需要进食!", style="yellow")
        if self.stats['hunger'] <= 0:
            damage = round(100 * random.uniform(0.75, 1.25))
            self.stats["hp"] -= damage
            console.print(f"你因饥饿受到了{damage}点伤害!", style="red")
            if self.stats["hp"] <= 0:
                console.print("你因饥饿而昏倒了...", style="red")
                self.alive = False

    def increase_max_hunger(self, amount):
        """
        增加最大饱食度。

        提高玩家的最大饱食度上限。

        参数:
            amount (int): 要增加的饱食度值
        """
        self.stats['max_hunger'] += amount
        print(f"最大饱食度增加了{amount}点! 现在是{self.stats['max_hunger']}")

    def rebirth(self, world_map):
        """
        玩家转生。

        将玩家重置为初始状态，但保留金钱、物品和职业。
        同时重置所有任务状态。这是游戏中的新游戏+机制。

        参数:
            world_map: 游戏世界地图对象，用于重置任务状态

        副作用:
            - 保存玩家的金钱、物品栏和职业
            - 重置玩家的所有属性和等级
            - 清空所有任务状态
            - 重置世界地图上的所有任务
        """
        print(fx.cyan("你选择了转生! 重置所有成长, 但保留了财富与物品"))
        self.unequip_all()
        saved_money, saved_inventory, saved_class = self.money, self.inventory, self.ls.class_name
        self.__init__(self.name)
        self.money, self.inventory, self.ls.class_name = saved_money, saved_inventory, saved_class
        self.active_quests.clear()
        self.completed_quests.clear()
        for region in world_map.regions.values():
            for q in region.quests:
                q.status = "Not Active"
        print(fx.cyan(f"你以 Lv.{self.ls.level} 重生，保留了 {self.money} 金币和背包物品!"))
        interface(self.inventory).show_inventory()

    def change_auto_mode(self):
        """
        切换自动战斗模式。

        开启或关闭玩家的自动战斗模式。
        在自动战斗模式下，玩家会自动执行基本战斗动作。
        """
        self.auto_mode = not self.auto_mode
        print("-Auto mode-")
