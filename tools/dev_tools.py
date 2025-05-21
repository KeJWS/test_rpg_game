"""
开发调试工具模块，提供用于游戏开发和测试的辅助功能。

该模块包含各种调试函数，包括调试信息输出、物品生成、背包操作等，
主要用于开发过程中的测试和调试。这些功能仅在DEBUG模式下可用。
"""

from data.constants import DEBUG

import os
import inspect
from datetime import datetime

import test.fx as fx

def debug_print(*args, **kwargs):
    """
    输出带有上下文信息的调试消息。

    在DEBUG模式下，打印包含时间戳、文件名和行号的调试信息。
    通过检查调用栈获取调用位置信息，帮助在调试时追踪消息来源。

    参数:
        *args: 要打印的可变参数列表
        **kwargs: 传递给print函数的关键字参数
    """
    if DEBUG:
        frame = inspect.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{fx.CYAN}[DEBUG {timestamp} {filename}:{lineno}]{fx.END}", *args, **kwargs)

def spawn_item(inventory_instance, item_name, quantity=1):
    """
    在指定背包中生成物品。

    根据提供的物品名称和数量，在背包中生成相应物品。
    支持生成装备、药水、宝石和魔法书等多种物品类型。
    如果找不到指定名称的物品，会输出警告信息。

    参数:
        inventory_instance: 要添加物品的背包实例
        item_name: 要生成的物品名称
        quantity: 要生成的物品数量，默认为1
    """
    from items import equipment_data, jewel_data, hp_potion, mp_potion, grimoires
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
        "atk_small_gems": jewel_data["atk_small_gems"],
        "mat_small_gems": jewel_data["mat_small_gems"],
        "agi_small_gems": jewel_data["agi_small_gems"],
        "crit_small_gems": jewel_data["crit_small_gems"],
        "atk_gems": jewel_data["atk_gems"],
        "mat_gems": jewel_data["mat_gems"],
        "agi_gems": jewel_data["agi_gems"],
        "crit_gems": jewel_data["crit_gems"],
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
    """
    在指定背包中生成所有类型的物品。

    向背包中添加游戏中所有类型的物品，包括所有装备、药水、宝石和魔法书。
    主要用于测试或快速填充玩家背包以进行游戏测试。

    参数:
        inventory_instance: 要添加物品的背包实例
    """
    from items import equipment_data, jewel_data, hp_potion, mp_potion, grimoires
    for eq in equipment_data.values():
        inventory_instance.add_item(eq.clone(amount=1))
    debug_print(f"已刷入 {len(equipment_data)} 件装备")

    potions = [hp_potion, mp_potion]
    for p in potions:
        inventory_instance.add_item(p.clone(amount=3))
    debug_print("已刷入全部药水")

    for j in jewel_data.values():
        inventory_instance.add_item(j.clone(amount=2))
    debug_print("已刷入全部宝石")

    for g in grimoires:
        inventory_instance.add_item(g.clone(amount=1))
    debug_print(f"已刷入 {len(grimoires)} 本魔法书")

def handle_debug_command(command, inventory_instance):
    """
    处理调试命令。

    解析和执行各种调试命令，如生成物品、生成所有物品或显示背包内容。
    命令格式包括：
    - "give [物品名] [数量]": 生成指定物品
    - "give-all": 生成所有物品
    - "bag": 显示背包内容

    参数:
        command: 要执行的调试命令字符串
        inventory_instance: 要操作的背包实例
    """
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
    """
    显示背包内容的简化视图。

    以调试格式打印背包中所有物品的列表，
    包括物品名称和数量，便于快速查看背包状态。

    参数:
        inv: 要显示内容的背包实例
    """
    print("\n[DEBUG] 当前背包物品：")
    for item in inv.items:
        print(f"- {item.name} x{item.amount}")
