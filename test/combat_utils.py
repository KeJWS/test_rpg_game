import time, sys
from typing import List

def battle_log(message: str, log_type: str = "info") -> None:
    """格式化战斗日志输出

    Args:
        message: 日志内容
        log_type: 日志类型('info', 'dmg', 'heal', 'crit', 'magic')
    """
    colors = {
        "info": "\033[36m",
        "dmg": "\033[31m",
        "heal": "\033[32m",
        "crit": "\033[33m",
        "magic": "\033[35m"
    }
    reset = "\033[0m"

    color = colors.get(log_type, colors["info"])
    print(f"{color}[战斗] {message}{reset}")

def select_objective(targets: List) -> None:
    """显示目标选择菜单

    Args:
        targets: 可选目标列表
    """
    print("\n选择目标:")
    for i, target in enumerate(targets, 1):
        hp_percent = round(target.stats["hp"] / target.stats["max_hp"] * 100)
        print(f"{i}. {target.name} - HP: {target.stats['hp']}/{target.stats['max_hp']} ({hp_percent}%)")

def get_valid_input(prompt: str, valid_range, cast_func=str):
    """获取有效输入

    Args:
        prompt: 提示信息
        valid_range: 有效值范围
        cast_func: 类型转换函数

    Returns:
        转换后的有效输入值
    """
    while True:
        try:
            val = cast_func(input(prompt))
            if val in valid_range:
                return val
        except:
            pass
        print("请输入有效选项")

def combat_menu(player, allies, enemies) -> None:
    """显示战斗菜单

    Args:
        player: 玩家角色
        allies: 盟友列表
        enemies: 敌人列表
    """
    print("\n" + "=" * 40)
    print(f"生命值: {player.stats['hp']}/{player.stats['max_hp']} | 魔法值: {player.stats['mp']}/{player.stats['max_mp']} | 连击点数: {player.combo_points}")

    # 显示敌人状态
    print("\n敌人:")
    for enemy in enemies:
        hp_percent = round(enemy.stats["hp"] / enemy.stats["max_hp"] * 100)
        hp_bar = "=" * (hp_percent // 5)
        print(f"{enemy.name}: [{hp_bar:<20}] {enemy.stats['hp']}/{enemy.stats['max_hp']} ({hp_percent}%)")

    print("\n战斗选项:")
    print("(A) 攻击 | (S) 施法 | (C) 连击 | (D) 防御 | (E) 逃跑")

def spell_menu(player) -> None:
    """显示法术菜单

    Args:
        player: 玩家角色
    """
    print("\n可用法术:")
    for i, spell in enumerate(player.spells, 1):
        print(f"{i}. {spell.name} (MP: {spell.cost}) - {spell.description}")
    print("0. 返回")

def combo_menu(player) -> None:
    """显示连击菜单

    Args:
        player: 玩家角色
    """
    print(f"\n可用连击 (当前CP: {player.combo_points}):")
    for i, combo in enumerate(player.combos, 1):
        print(f"{i}. {combo.name} (CP: {combo.cost}) - {combo.description}")
    print("0. 返回")

def display_status_effects(battlers: List) -> None:
    """显示所有战斗单位的状态效果

    Args:
        battlers: 战斗单位列表
    """
    has_effects = False
    for battler in battlers:
        if battler.buffs_and_debuffs:
            has_effects = True
            print(f"\n{battler.name} 的状态效果:")
            for buff in battler.buffs_and_debuffs:
                effect_type = "增益" if buff.amount_to_change > 0 else "减益"
                print(f"  {buff.name}: {effect_type} {buff.stat_to_change} ({buff.turns} 回合)")

    if has_effects:
        print("-" * 40)

# def dot_loading(duration: float = 0.3) -> None:
#     """显示加载动画

#     Args:
#         duration: 动画持续时间(秒)
#     """
#     dots = ['', '.', '..', '...']
#     start_time = time.time()
#     i = 0

#     while time.time() - start_time < duration:
#         print(f"\r加载中{dots[i % len(dots)]}", end="")
#         time.sleep(0.2)
#         i += 1

#     print("\r" + " " * 20 + "\r", end="")

# def typewriter(text: str, speed: float = 0.02) -> None:
#     """打字机效果显示文本

#     Args:
#         text: 要显示的文本
#         speed: 每个字符间的延迟(秒)
#     """
#     for char in text:
#         sys.stdout.write(char)
#         sys.stdout.flush()
#         time.sleep(speed)
#     print()
