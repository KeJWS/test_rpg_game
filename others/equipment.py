import os
import random
import ascii_magic
from typing import Dict, List, Optional, Tuple, Union, Any

import test.fx as fx
import data.constants as constants
from others.item import Item

class Equipment(Item):
    # Quality definitions: (name, price_multiplier, stat_multiplier, chance_weight)
    QUALITY_CONFIG: List[Tuple[str, float, float, int]] = [
        ("生锈的", 0.5, 0.75, 25),
        ("普通的", 1.0, 1.0, 50),
        ("优质的", 2.2, 1.35, 13),
        ("魔法的", 4.5, 1.75, 9),
        ("传奇的", 12.0, 2.35, 3)
    ]

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
        super().__init__(name, description, amount, individual_value, object_type)
        self.base_stats: Dict[str, int] = stat_change_list.copy()
        self.base_value: int = individual_value
        self.base_name: str = name
        self.stat_change_list: Dict[str, int] = self.base_stats.copy()
        self.combo = combo
        self.spell = spell
        self.level = level
        self.tags = tags or []

        if quality_data:
            self.quality, self.quality_price_multiplier, self.quality_stat_multiplier = quality_data
        else:
            self.quality, self.quality_price_multiplier, self.quality_stat_multiplier = self._generate_quality()

        if apply_quality:
            self._apply_quality()

        self.name = f"{self.quality}{self.name}"

        self.individual_value = int(self.base_value * self.quality_price_multiplier)
        self.image_path: str = image_path or constants.DEFAULT_EQUIPMENT_IMAGES.get(
            object_type, "data/equipments/default_unknown.png"
        )

    def _generate_quality(self) -> Tuple[str, float, float]:
        roll = random.randint(1, 100)
        for name, price_mult, stat_mult, weight in self.QUALITY_CONFIG:
            if roll <= weight:
                return name, price_mult, stat_mult
            roll -= weight
        return "普通的", 1.0, 1.0

    def _apply_quality(self) -> None:
        for key, val in self.base_stats.items():
            self.base_stats[key] = int(val * self.quality_stat_multiplier)
        self.stat_change_list = self.base_stats.copy()

    def display_image_as_ascii(self) -> str:
        if not self.image_path or not os.path.exists(self.image_path):
            return "[图片缺失]"
        art = ascii_magic.AsciiArt.from_image(self.image_path)
        return art.to_ascii(columns=32)

    def show_stats(self) -> str:
        parts = []
        for stat, val in self.stat_change_list.items():
            sign = "+" if val >= 0 else ""
            parts.append(f"{stat} {sign}{val}")
        return "[green][ " + " ".join(parts) + " ][/green]"

    def show_info(self):
        combo_name = f"[yellow]{self.combo.name}[/yellow]" if self.combo else ""
        spell_name = f"[yellow]{self.spell.name}[/yellow]" if self.spell else ""
        return (
            f"[x{self.amount}] {self.name} ({self.object_type}) {self.show_stats()} - "
            f"{self.individual_value}G {combo_name}{spell_name}\n"
            f"    简介: {self.description}"
        )

    def get_detailed_info(self) -> str:
        info = super().get_detailed_info()
        info += f"{self.display_image_as_ascii()}\n"
        info += f"品质: {fx.YELLO}{self.quality}{fx.END}\n"
        info += "属性加成:\n"
        for stat, value in self.stat_change_list.items():
            sign = "+" if value >= 0 else ""
            info += f"  {fx.GREEN}{stat}: {sign}{value}{fx.END}\n"
        return info

    def compare_with(self, other: Any) -> str:
        if not isinstance(other, Equipment):
            return "无法比较不同类型的物品"
        my = self.stat_change_list
        oth = other.stat_change_list
        lines = [f"比较 {self.name} vs {other.name}:\n"]
        for stat in sorted(set(my) | set(oth)):
            diff = my.get(stat, 0) - oth.get(stat, 0)
            sign = "+" if diff >= 0 else ""
            lines.append(f"  {stat}: {my.get(stat,0)} ({sign}{diff})")
        return "\n".join(lines)

    def reroll_quality(self):
        self.quality, self.quality_price_multiplier, self.quality_stat_multiplier = self._generate_quality()
        self._apply_quality()
        self.name = f"{self.quality}{self.base_name}"
        self.individual_value = int(self.base_value * self.quality_price_multiplier)

    def clone(self, amount: int) -> 'Equipment':
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
            quality_data=(self.quality, self.quality_price_multiplier, self.quality_stat_multiplier),
            apply_quality=False,
        )
        clone.stat_change_list = self.stat_change_list.copy()
        return clone
