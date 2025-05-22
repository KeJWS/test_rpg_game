"""
装备系统模块，定义游戏中可装备物品的基类和功能。

该模块实现了装备系统的核心功能，包括装备的品质、属性效果、
比较和克隆等。装备是游戏中提升角色能力的重要物品类型，
具有不同品质等级和属性加成。
"""

import random
import ascii_magic
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from rich.console import Console

import data.constants as constants
from others.item import Item

console = Console()

class Equipment(Item):
    """
    装备类，代表游戏中可装备的物品。

    扩展基础物品类，添加装备特有的属性如品质系统、属性修正、套装效果等。
    装备可以提升角色的各项属性，有不同的品质等级影响其属性加成强度。

    属性:
        base_name (str): 装备的基础名称
        base_stats (Dict[str, int]): 基础属性加成，不受品质影响
        base_value (int): 基础价值
        stat_change_list (Dict[str, int]): 最终属性加成，受品质影响
        combo (Any): 关联的套装效果
        spell (Any): 关联的法术效果
        level (int): 装备等级
        tags (List[str]): 装备标签
        quality (str): 装备品质
        price_mult (float): 品质对价格的影响系数
        stat_mult (float): 品质对属性加成的影响系数
        image_path (str): 装备图像路径
    """
    QUALITY_CONFIG = constants.QUALITY_CONFIG

    def __init__(
        self,
        name: str,
        description: str,
        amount: int,
        individual_value: int,
        object_type: str,
        stat_change_list: Dict[str, int],
        combo: Optional[Any] = None,
        spell: Optional[Any] = None,
        level: int = 1,
        tags: Optional[List[str]] = None,
        image_path: Optional[str] = None,
        quality_data: Optional[Tuple[str, float, float]] = None,
        apply_quality: bool = True,
    ):
        """
        初始化装备实例。

        创建一个新的装备对象，设置其基本属性和装备特有属性，
        如果未提供品质数据，则随机生成品质并应用。

        参数:
            name (str): 装备名称
            description (str): 装备描述
            amount (int): 数量
            individual_value (int): 单个装备的基础价值
            object_type (str): 装备类型，如"weapon"、"armor"等
            stat_change_list (Dict[str, int]): 装备提供的属性变化
            combo (Any, optional): 装备关联的套装，默认为None
            spell (Any, optional): 装备关联的法术，默认为None
            level (int, optional): 装备等级，默认为1
            tags (List[str], optional): 装备标签，默认为空列表
            image_path (str, optional): 装备图像路径，默认为None
            quality_data (Tuple[str, float, float], optional): 品质数据，默认为None
            apply_quality (bool, optional): 是否应用品质效果，默认为True
        """
        super().__init__(name, description, amount, individual_value, object_type)
        self.base_name = name
        self.base_stats = stat_change_list.copy()
        self.base_value = individual_value
        self.stat_change_list = self.base_stats.copy()
        self.combo = combo
        self.spell = spell
        self.level = level
        self.tags = tags or []

        self.quality, self.price_mult, self.stat_mult = quality_data if quality_data else self._generate_quality()

        if apply_quality:
            self._apply_quality()

        self.name = f"{self.quality}{self.base_name}"
        self.individual_value = int(self.base_value * self.price_mult)
        self.image_path = image_path or constants.DEFAULT_EQUIPMENT_IMAGES.get(
            object_type, "img/equipments/default_unknown.png"
        )

    def _generate_quality(self) -> Tuple[str, float, float]:
        """
        根据预设权重随机生成装备品质。

        从预设的品质配置中，根据各品质的权重概率随机选择一个品质，
        返回该品质的名称、价格乘数和属性乘数。

        返回:
            Tuple[str, float, float]: 包含(品质名称, 价格乘数, 属性乘数)的元组
        """
        names, price_ms, stat_ms, weights = zip(*self.QUALITY_CONFIG)
        idx = random.choices(range(len(names)), weights=weights, k=1)[0]
        return names[idx], price_ms[idx], stat_ms[idx]

    def _apply_quality(self) -> None:
        """
        根据装备品质修正属性加成。

        应用品质系数到装备的基础属性上，计算最终的属性加成值。
        这将根据品质的不同，调整装备的实际属性效果强度。

        副作用:
            修改stat_change_list字典中的值
        """
        for key, val in self.base_stats.items():
            self.stat_change_list[key] = int(val * self.stat_mult)

    def display_image_as_ascii(self) -> str:
        """
        将装备图像转换为ASCII艺术展示。

        读取装备的图像文件，将其转换为ASCII字符组成的文本图像，
        便于在终端中展示装备的视觉外观。

        返回:
            str: ASCII字符组成的图像字符串

        异常:
            如果图像文件不存在，返回错误提示
        """
        path = Path(self.image_path)
        if not path.is_file():
            return "[图片缺失]"
        art = ascii_magic.AsciiArt.from_image(self.image_path)
        return art.to_ascii(columns=32)

    def show_stats(self) -> str:
        """
        生成装备属性加成的格式化文本。

        将装备的所有属性加成转换为易读的格式，
        以"属性名 +/-值"的形式显示，用绿色标记。

        返回:
            str: 格式化的属性加成文本
        """
        parts = [f"{stat} {val:+d}" for stat, val in self.stat_change_list.items()]
        return "[green][ " + " ".join(parts) + " ][/green]"

    def show_info(self):
        """
        生成装备的简要信息描述。

        创建一个包含装备名称、类型、属性加成、价值、
        套装、法术和简介的格式化字符串，用于在库存中展示。

        返回:
            str: 格式化的装备信息字符串
        """
        combo_name = f"[yellow]{self.combo.name}[/yellow]" if self.combo else ""
        spell_name = f"[yellow]{self.spell.name}[/yellow]" if self.spell else ""
        return (
            f"[x{self.amount}] {self.name} ({self.object_type}) {self.show_stats()} - "
            f"{self.individual_value}G {combo_name}{spell_name}\n"
            f"    简介: {self.description}"
        )

    def get_detailed_info(self) -> str:
        """
        生成装备的详细信息描述。

        创建一个包含装备基本信息、ASCII图像、品质和所有属性加成
        的详细文本描述，用于查看装备的完整信息。

        返回:
            str: 包含多行详细信息的字符串
        """
        info = [super().get_detailed_info(), self.display_image_as_ascii()]
        info.append(f"品质: \033[33m{self.quality}\033[0m")
        info.append("属性加成:")
        for stat, val in self.stat_change_list.items():
            info.append(f"  \033[32m{stat}: {val:+d}\033[0m")
        return "\n".join(info)

    def compare_with(self, other: Any) -> str:
        """
        比较两件装备的属性差异。

        将此装备与另一件装备的所有属性进行比较，显示每个属性的差异值。
        如果比较对象不是装备类型，则返回错误信息。

        参数:
            other (Any): 要与之比较的另一个对象，应为Equipment类型

        返回:
            str: 包含装备比较结果的格式化字符串
        """
        if not isinstance(other, Equipment):
            return "无法比较不同类型的物品"
        keys = sorted(set(self.stat_change_list) | set(other.stat_change_list))
        lines = [f"比较 {self.name} vs {other.name}:"]
        lines += [
            f"  {s}: {self.stat_change_list.get(s,0)} ({self.stat_change_list.get(s,0)-other.stat_change_list.get(s,0):+d})"
            for s in keys
        ]
        return "\n".join(lines)

    def reroll_quality(self):
        """
        重新随机生成装备品质并应用。

        重新随机选择装备的品质，并根据新品质更新装备名称、
        属性加成和价值。可用于商店物品生成或装备升级系统。

        副作用:
            - 修改装备的品质、价值和属性加成
            - 更新装备名称
        """
        self.quality, self.price_mult, self.stat_mult = self._generate_quality()
        self._apply_quality()
        self.name = f"{self.quality}{self.base_name}"
        self.individual_value = int(self.base_value * self.price_mult)

    def clone(self, amount: int) -> 'Equipment':
        """
        创建此装备的副本。

        创建一个具有相同属性但可能不同数量的新装备实例。
        克隆保留原装备的所有属性，包括品质、属性加成等。

        参数:
            amount (int): 新装备实例的数量

        返回:
            Equipment: 此装备的副本
        """
        clone = self.__class__(
            name=self.base_name,
            description=self.description,
            amount=amount,
            individual_value=self.base_value,
            object_type=self.object_type,
            stat_change_list=self.base_stats.copy(),
            combo=self.combo,
            spell=self.spell,
            level=self.level,
            tags=self.tags.copy(),
            image_path=self.image_path,
            quality_data=(self.quality, self.price_mult, self.stat_mult),
            apply_quality=False,
        )
        clone.stat_change_list = self.stat_change_list.copy()
        return clone
