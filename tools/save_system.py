"""
存档系统模块，提供游戏进度的保存与加载功能。

该模块实现了完整的存档系统，包括将玩家数据序列化为JSON格式存储、
从JSON数据还原玩家对象、管理存档文件以及提供存档列表查询等功能。
支持玩家角色的所有属性、背包物品、技能和状态的保存与恢复。
"""

import json
import os
import time

from player import Player
import others.item as other
from others.equipment import Equipment

SAVE_FOLDER = "saves"

def ensure_save_folder():
    """
    确保存档文件夹存在。

    检查存档文件夹是否存在，如果不存在则创建。
    这是一个辅助函数，用于在保存或加载游戏前确保存档目录已准备好。
    """
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def player_to_dict(player):
    """
    将玩家对象转换为可序列化的字典。

    将Player对象的所有相关属性转换为JSON可序列化的字典格式，
    包括基本属性、统计数据、物品栏内容和技能等。处理各种物品类型，
    确保所有复杂对象都被正确转换为简单数据类型。

    参数:
        player: 要转换的玩家对象

    返回:
        dict: 表示玩家数据的字典，可用于JSON序列化
    """
    player_dict = {
        "name": player.name,
        "class_name": player.ls.class_name,
        "level": player.ls.level,
        "xp": player.ls.xp,
        "xp_to_next_level": player.ls.xp_to_next_level,
        "stats": player.stats,
        "aptitudes": player.aptitudes,
        "aptitude_points": player.ls.aptitude_points,
        "buffs_and_debuffs": [],
        "is_ally": player.is_ally,
        "is_defending": player.is_defending,
        "alive": player.alive,
        "money": player.money,
        "inventory": [],
        "spells": [spell.name for spell in player.spells],
    }

    # 保存库存物品
    for item in player.inventory.items:
        item_dict = {
            "type": item.__class__.__name__,
            "name": item.name,
            "description": item.description,
            "amount": item.amount,
            "individual_value": item.individual_value,
            "object_type": item.object_type,
        }

        # 处理特定项目类型
        if item.__class__.__name__ == "Equipment":
            item_dict["stat_change_list"] = item.stat_change_list
            item_dict["combo"] = item.combo.name if hasattr(item.combo, "name") else str(item.combo)
            item_dict["ascii_art"] = item.ascii_art
            item_dict["level"] = item.level
            item_dict["tags"] = item.tags
        elif item.__class__.__name__ == "Potion":
            item_dict["stat"] = item.stat
            item_dict["amount_to_change"] = item.amount_to_change
        elif item.__class__.__name__ == "Grimoire":
            item_dict["spell"] = item.spell.name if hasattr(item.spell, "name") else str(item.spell)
        elif item.__class__.__name__ == "Jewel":
            item_dict["stat"] = item.stat
            item_dict["amount_to_change"] = item.amount_to_change

        player_dict["inventory"].append(item_dict)

    return player_dict

def dict_to_player(player_dict):
    """
    将字典转换回玩家对象。

    从字典数据重新构建Player对象，包括恢复所有属性、装备、
    物品栏和技能。这是player_to_dict的逆操作，用于从存档加载游戏。

    参数:
        player_dict: 包含玩家数据的字典，通常来自存档文件

    返回:
        Player: 重建的玩家对象实例，包含所有恢复的数据和状态
    """
    import skills

    # 恢复咒语（参考预定义咒语）
    spell_mapping = {
        "火球术": skills.spell_fire_ball,
        "神圣祝福": skills.spell_divine_blessing,
        "强化武器": skills.spell_enhance_weapon,
        "地狱火": skills.spell_inferno,
        "召唤骷髅": skills.spell_skeleton_summoning,
        "召唤火精灵": skills.spell_fire_spirit_summoning,
    }

    combo_mapping = {
        "斩击连击 I": skills.combo_slash1,
        "斩击连击 II": skills.combo_slash2,
        "破甲 I": skills.combo_armor_breaker1,
        "吸血之刺 I": skills.combo_vampire_stab1,
        "吸血之刺 II": skills.combo_vampire_stab2,
        "冥想 I": skills.combo_meditation1,
        "冥想 II": skills.combo_meditation2,
        "快速连射 I": skills.combo_quickSshooting1,
        "快速连射 II": skills.combo_quickSshooting2,
    }

    player = Player(player_dict["name"])
    player.ls.class_name = player_dict["class_name"]
    player.ls.level = player_dict["level"]
    player.ls.xp = player_dict["xp"]
    player.ls.xp_to_next_level = player_dict["xp_to_next_level"]
    player.stats = player_dict["stats"]
    player.aptitudes = player_dict["aptitudes"]
    player.ls.aptitude_points = player_dict["aptitude_points"]
    player.is_ally = player_dict["is_ally"]
    player.is_defending = player_dict["is_defending"]
    player.alive = player_dict["alive"]
    player.money = player_dict["money"]

    player.inventory.items = []

    # 恢复库存
    for item_dict in player_dict["inventory"]:
        if item_dict["type"] == "Equipment":
            combo_obj = combo_mapping.get(item_dict["combo"])
            item = Equipment(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                item_dict["stat_change_list"],
                combo_obj,
                item_dict["ascii_art"],
                item_dict["level"],
                item_dict["tags"],
            )
        elif item_dict["type"] == "Potion":
            item = other.Potion(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                item_dict["stat"],
                item_dict["amount_to_change"]
            )
        elif item_dict["type"] == "Grimoire":
            spell_obj = spell_mapping.get(item_dict["spell"])
            item = other.Grimoire(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                spell_obj
            )
        elif item_dict["type"] == "Jewel":
            item = other.Jewel(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                item_dict["stat"],
                item_dict["amount_to_change"]
            )
        else:
            item = other.Item(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"]
            )
        player.inventory.items.append(item)
    
    player.spells = [spell_mapping.get(spell_name) for spell_name in player_dict["spells"] if spell_name in spell_mapping]

    return player

def save_game(player, save_name=None):
    """
    保存游戏进度到文件。

    将当前玩家状态保存到JSON文件中，包含完整的玩家数据和存档元数据。
    如果未提供存档名称，将使用时间戳生成默认名称。

    参数:
        player: 要保存的玩家对象
        save_name: 可选的存档名称，默认为使用时间戳的自动生成名称

    返回:
        dict: 包含存档元数据的字典，包括名称、玩家名、等级和时间戳等
    """
    ensure_save_folder()

    if not save_name:
        save_name = f"save_{int(time.time())}"

    # 创建保存的元数据
    save_metadata = {
        "name": save_name,
        "player_name": player.name,
        "level": player.ls.level,
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 将玩家转换为字典以进行 JSON 序列化
    player_dict = player_to_dict(player)

    # 创建一个包含元数据和玩家数据的 JSON 文件
    save_data = {
        "metadata": save_metadata,
        "player_data": player_dict
    }

    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.json")
    with open(save_path, "w", encoding="utf-8") as save_file:
        json.dump(save_data, save_file, ensure_ascii=False, indent=2)

    return save_metadata

# TODO 读档以后任务会清空
def load_game(save_name):
    """
    从存档文件加载游戏进度。

    根据提供的存档名称，从对应的JSON文件中读取游戏数据，
    并将其转换回Player对象。如果存档不存在或加载过程中出错，
    将返回None并显示错误信息。

    参数:
        save_name: 要加载的存档名称

    返回:
        Player: 从存档恢复的玩家对象，如果加载失败则返回None

    异常:
        捕获并处理所有可能的异常，将错误信息打印到控制台
    """
    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.json")
    if not os.path.exists(save_path):
        print(f"存档 '{save_name}' 不存在")
        return None

    try:
        with open(save_path, "r", encoding="utf-8") as save_file:
            save_data = json.load(save_file)

        player = dict_to_player(save_data["player_data"])
        return player
    except Exception as e:
        print(f"加载存档失败: {e}")
        return None

def get_save_list():
    """
    获取所有有效存档的列表。

    扫描存档文件夹，读取所有有效的.json存档文件，提取其元数据信息，
    并按时间戳倒序排列（最新的存档排在前面）。

    返回:
        list: 存档元数据字典的列表，每个字典包含名称、玩家名、等级和时间戳等信息
    """
    ensure_save_folder()
    saves = []

    for filename in os.listdir(SAVE_FOLDER):
        if filename.endswith(".json"):
            save_path = os.path.join(SAVE_FOLDER, filename)
            try:
                with open(save_path, "r", encoding="utf-8") as save_file:
                    save_data = json.load(save_file)
                    saves.append(save_data["metadata"])
            except:
                # 跳过无效文件
                continue

    saves.sort(key=lambda x: x["timestamp"], reverse=True)
    return saves
