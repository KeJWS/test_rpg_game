"""
战斗辅助工具模块，提供战斗系统使用的各种界面和功能函数。

该模块包含战斗系统所需的各种辅助功能，如战斗日志输出、目标选择、
战斗菜单显示、法术菜单、连击菜单等。这些功能共同支持游戏的战斗系统，
提供了用户交互界面和战斗状态展示。
"""

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
