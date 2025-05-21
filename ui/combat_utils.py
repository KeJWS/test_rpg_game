"""
战斗辅助工具模块，提供战斗系统使用的各种界面和功能函数。

该模块包含战斗系统所需的各种辅助功能，如战斗日志输出、目标选择、
战斗菜单显示、法术菜单、连击菜单等。这些功能共同支持游戏的战斗系统，
提供了用户交互界面和战斗状态展示。
"""

from typing import List

def battle_log(message: str, log_type: str = "info") -> None:
    """
    格式化战斗日志输出。

    根据日志类型添加不同颜色，增强战斗日志可读性，
    帮助玩家区分不同类型的战斗信息。

    参数:
        message (str): 需要输出的日志内容
        log_type (str, optional): 日志类型，可选值包括
            'info'(信息), 'dmg'(伤害), 'heal'(治疗),
            'crit'(暴击), 'magic'(魔法)，默认为'info'

    副作用:
        在控制台输出带颜色的战斗日志
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
    """
    显示战斗目标选择菜单。

    展示可选择的战斗目标列表，包括目标名称和当前生命值状态，
    帮助玩家在战斗中选择攻击或技能的目标。

    参数:
        targets (List): 可选战斗目标列表，每个目标应具有name和stats属性

    副作用:
        在控制台输出目标选择菜单
    """
    print("\n选择目标:")
    for i, target in enumerate(targets, 1):
        hp_percent = round(target.stats["hp"] / target.stats["max_hp"] * 100)
        print(f"{i}. {target.name} - HP: {target.stats['hp']}/{target.stats['max_hp']} ({hp_percent}%)")

def get_valid_input(prompt: str, valid_range, cast_func=str):
    """
    获取用户有效输入。

    提示用户输入，验证输入是否在有效范围内，
    支持类型转换，并在输入无效时重新提示，
    确保获取到有效的用户输入。

    参数:
        prompt (str): 显示给用户的提示信息
        valid_range: 有效值的范围或集合，用于验证输入是否有效
        cast_func (function, optional): 输入值的类型转换函数，默认为str

    返回:
        转换后的有效输入值，类型由cast_func决定

    异常:
        捕获所有异常但不向上抛出，而是提示用户重新输入
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
    """
    显示战斗主菜单。

    展示当前战斗状态，包括玩家状态、敌人状态和可用的战斗选项，
    是战斗系统的主界面，提供战斗中的主要决策选项。

    参数:
        player: 玩家角色对象，必须包含stats和combo_points属性
        allies: 盟友角色列表
        enemies: 敌人角色列表，每个敌人必须包含name和stats属性

    副作用:
        在控制台输出战斗状态和选项菜单
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
    """
    显示玩家可用法术菜单。

    展示玩家当前可用的所有法术及其描述和魔法消耗，
    让玩家在战斗中选择要施放的法术。

    参数:
        player: 玩家角色对象，必须包含spells属性(法术列表)

    副作用:
        在控制台输出法术选择菜单
    """
    print("\n可用法术:")
    for i, spell in enumerate(player.spells, 1):
        print(f"{i}. {spell.name} (MP: {spell.cost}) - {spell.description}")
    print("0. 返回")

def combo_menu(player) -> None:
    """
    显示玩家可用连击技能菜单。

    展示玩家当前可用的所有连击技能及其描述和连击点数消耗，
    让玩家在积累足够连击点数后选择要使用的连击技能。

    参数:
        player: 玩家角色对象，必须包含combos属性(连击技能列表)和combo_points属性

    副作用:
        在控制台输出连击技能选择菜单
    """
    print(f"\n可用连击 (当前CP: {player.combo_points}):")
    for i, combo in enumerate(player.combos, 1):
        print(f"{i}. {combo.name} (CP: {combo.cost}) - {combo.description}")
    print("0. 返回")

def display_status_effects(battlers: List) -> None:
    """
    显示所有战斗单位的状态效果。

    展示战斗中所有单位(玩家、盟友、敌人)当前所受的状态效果，
    包括增益和减益效果、影响的属性以及剩余回合数。

    参数:
        battlers (List): 战斗单位列表，每个单位必须包含name和buffs_and_debuffs属性

    副作用:
        在控制台输出所有战斗单位的状态效果信息
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
#     """
#     显示点状加载动画。

#     在控制台显示简单的点状加载动画，提示用户等待，
#     动画结束后会清除所显示的内容。

#     参数:
#         duration (float, optional): 动画持续时间，单位为秒，默认为0.3秒

#     副作用:
#         在控制台显示动态变化的加载动画
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
#     """
#     以打字机效果显示文本。

#     逐字符地显示文本，产生类似打字机的视觉效果，
#     增强游戏中对话和叙事的沉浸感。

#     参数:
#         text (str): 要显示的文本内容
#         speed (float, optional): 每个字符显示之间的延迟，单位为秒，默认为0.02秒

#     副作用:
#         在控制台以打字机效果逐字符显示文本
#     """
#     for char in text:
#         sys.stdout.write(char)
#         sys.stdout.flush()
#         time.sleep(speed)
#     print()
