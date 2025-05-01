import random
import ascii_magic
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import test.fx as fx
import data.constants as constants
from others.item import Item

class Equipment(Item):
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
            object_type, "assests/equipments/default_unknown.png"
        )

    def _generate_quality(self) -> Tuple[str, float, float]:
        """根据权重随机选择"""
        names, price_ms, stat_ms, weights = zip(*self.QUALITY_CONFIG)
        idx = random.choices(range(len(names)), weights=weights, k=1)[0]
        return names[idx], price_ms[idx], stat_ms[idx]

    def _apply_quality(self) -> None:
        """根据品质修正属性"""
        for key, val in self.base_stats.items():
            self.base_stats[key] = int(val * self.stat_mult)
        self.stat_change_list = self.base_stats.copy()

    def display_image_as_ascii(self) -> str:
        path = Path(self.image_path)
        if not path.is_file():
            return "[图片缺失]"
        art = ascii_magic.AsciiArt.from_image(self.image_path)
        return art.to_ascii(columns=32)

    def show_stats(self) -> str:
        parts = [f"{stat} {val:+d}" for stat, val in self.stat_change_list.items()]
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
        info = [super().get_detailed_info(), self.display_image_as_ascii()]
        info.append(f"品质: {fx.YELLO}{self.quality}{fx.END}")
        info.append("属性加成:")
        for stat, val in self.stat_change_list.items():
            info.append(f"  {fx.GREEN}{stat}: {val:+d}{fx.END}")
        return "\n".join(info)

    def compare_with(self, other: Any) -> str:
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
        """重置品质并应用"""
        self.quality, self.price_mult, self.stat_mult = self._generate_quality()
        self._apply_quality()
        self.name = f"{self.quality}{self.base_name}"
        self.individual_value = int(self.base_value * self.price_mult)

    def clone(self, amount: int) -> 'Equipment':
        return self.__class__(
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
