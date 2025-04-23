from data.constants import DEBUG

import os
from datetime import datetime
import inspect

import test.fx as fx
from items import atk_gems, mat_gems, agi_gems, crit_gems, grimoires
from items import equipment_data, hp_potion, mp_potion, atk_small_gems, mat_small_gems, agi_small_gems, crit_small_gems

def debug_print(*args, **kwargs):
    if DEBUG:
        frame = inspect.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{fx.CYAN}[DEBUG {timestamp} {filename}:{lineno}]{fx.END}", *args, **kwargs)

def spawn_item(inventory_instance, item_name, quantity=1):
    # 查找装备
    if item_name in equipment_data:
        eq = equipment_data[item_name]
        for _ in range(quantity):
            inventory_instance.add_item(eq.clone(amount=quantity))
        debug_print(f"刷入装备：{item_name} x{quantity}")
        return

    # 查找药水、宝石或魔法书
    item_map = {
        "hp_potion": hp_potion,
        "mp_potion": mp_potion,
        "atk_small_gems": atk_small_gems,
        "mat_small_gems": mat_small_gems,
        "agi_small_gems": agi_small_gems,
        "crit_small_gems": crit_small_gems,
        "atk_gems": atk_gems,
        "mat_gems": mat_gems,
        "agi_gems": agi_gems,
        "crit_gems": crit_gems,
    }

    for g in grimoires:
        item_map[g.name] = g

    if item_name in item_map:
        for _ in range(quantity):
            inventory_instance.add_item(item_map[item_name].clone())
        debug_print(f"刷入物品：{item_name} x{quantity}")
    else:
        debug_print(f"[警告] 找不到名为 {item_name} 的物品")

def spawn_all_items(inventory_instance):
    for eq in equipment_data.values():
        inventory_instance.add_item(eq.clone(amount=1))
    debug_print(f"已刷入 {len(equipment_data)} 件装备")

    potions = [hp_potion, mp_potion]
    for p in potions:
        inventory_instance.add_item(p.clone(amount=3))
    debug_print("已刷入全部药水")

    jewels = [
        atk_small_gems, mat_small_gems, agi_small_gems, crit_small_gems,
        atk_gems, mat_gems, agi_gems, crit_gems
    ]
    for j in jewels:
        inventory_instance.add_item(j.clone(amount=2))
    debug_print("已刷入全部宝石")

    for g in grimoires:
        inventory_instance.add_item(g.clone(amount=1))
    debug_print(f"已刷入 {len(grimoires)} 本魔法书")

def handle_debug_command(command, inventory_instance):
    if not DEBUG:
        return
    command = command.strip().lower()
    if command.startswith("give "):
        parts = command.split()
        item_name = parts[1]
        quantity = int(parts[2]) if len(parts) > 2 else 1
        spawn_item(inventory_instance, item_name, quantity)
    elif command == "give-all":
        spawn_all_items(inventory_instance)
    elif command == "bag":
        debug_show_inventory(inventory_instance)
    else:
        debug_print(f"未知指令: {command}")

def debug_show_inventory(inv):
    print("\n[DEBUG] 当前背包物品：")
    for item in inv.items:
        print(f"- {item.name} x{item.amount}")
