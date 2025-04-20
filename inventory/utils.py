
def prompt_for_amount(max_amount, prompt="多少个？") -> int:
    """提示用户输入数量并进行验证"""
    try:
        amount = int(input(f"{prompt} (最多: {max_amount})\n> "))
        if 0 < amount <= max_amount:
            return amount
        print(f"请输入 1 到 {max_amount} 之间的数字!")
    except ValueError:
        print("请输入有效数字!")
    return 0

def select_item_from_list(item_list, prompt="选择一个物品:", allow_exit=True):
    """显示项目列表并提示用户选择一个"""
    if not item_list:
        print("没有可选择的物品")
        return None

    print(f"\n{prompt} {['', '[输入 0 退出]'][allow_exit]}")
    for index, item in enumerate(item_list, start=1):
        print(f"{index}. {item.show_info()}")

    while True:
        choice = input("> ")
        if choice == "0" and allow_exit:
            print("退出...")
            return None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(item_list):
                return item_list[choice_num - 1]
        print("无效输入")
