import json
import os
import time

from player import Player

SAVE_FOLDER = "saves"

def ensure_save_folder():
    """确保存档文件夹存在"""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def player_to_dict(player):
    """将玩家对象转换为 JSON 可序列化字典"""
    player_dict = {
        "name": player.name,
        "class_name": player.class_name,
        "level": player.level,
        "xp": player.xp,
        "xp_to_next_level": player.xp_to_next_level,
        "stats": player.stats,
        "aptitudes": player.aptitudes,
        "aptitude_points": player.aptitude_points,
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
    """Convert dictionary back to Player object"""
    import inventory, skills

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
    player.class_name = player_dict["class_name"]
    player.level = player_dict["level"]
    player.xp = player_dict["xp"]
    player.xp_to_next_level = player_dict["xp_to_next_level"]
    player.stats = player_dict["stats"]
    player.aptitudes = player_dict["aptitudes"]
    player.aptitude_points = player_dict["aptitude_points"]
    player.is_ally = player_dict["is_ally"]
    player.is_defending = player_dict["is_defending"]
    player.alive = player_dict["alive"]
    player.money = player_dict["money"]

    player.inventory.items = []

    # 恢复库存
    for item_dict in player_dict["inventory"]:
        if item_dict["type"] == "Equipment":
            combo_obj = combo_mapping.get(item_dict["combo"])
            item = inventory.Equipment(
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
            item = inventory.Potion(
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
            item = inventory.Grimoire(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                spell_obj
            )
        elif item_dict["type"] == "Jewel":
            item = inventory.Jewel(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                item_dict["stat"],
                item_dict["amount_to_change"]
            )
        else:
            item = inventory.Item(
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
    """保存游戏进度"""
    ensure_save_folder()

    if not save_name:
        save_name = f"save_{int(time.time())}"

    # 创建保存的元数据
    save_metadata = {
        "name": save_name,
        "player_name": player.name,
        "level": player.level,
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
    """加载游戏存档"""
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
    """获取所有存档列表"""
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
