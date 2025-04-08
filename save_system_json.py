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
        "level": player.level,
        "xp": player.xp,
        "xp_to_next_level": player.xp_to_next_level,
        "stats": player.stats,
        "aptitudes": player.aptitudes,
        "aptitude_points": player.aptitude_points,
        "buffs_and_debuffs": [], # 不保存增益效果，因为它们是暂时的
        "is_ally": player.is_ally,
        "is_defending": player.is_defending,
        "alive": player.alive,
        "money": player.money,
        "inventory": [],
        "equipment": {"weapon": None, "armor": None},
        "spells": [spell.name for spell in player.spells]
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
        elif item.__class__.__name__ == "Potion":
            item_dict["stat"] = item.stat
            item_dict["amount_to_change"] = item.amount_to_change
            
        player_dict["inventory"].append(item_dict)
    
    # 保存装备
    for slot, equipment in player.equipment.items():
        if equipment:
            equip_dict = {
                "name": equipment.name,
                "description": equipment.description,
                "amount": equipment.amount,
                "individual_value": equipment.individual_value,
                "object_type": equipment.object_type,
                "stat_change_list": equipment.stat_change_list
            }
            player_dict["equipment"][slot] = equip_dict
    
    return player_dict

def dict_to_player(player_dict):
    """Convert dictionary back to Player object"""
    import inventory, skills
    
    player = Player(player_dict["name"])
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
    
    # 清除默认库存
    player.inventory.items = []
    
    # 恢复库存
    for item_dict in player_dict["inventory"]:
        if item_dict["type"] == "Equipment":
            item = inventory.Equipment(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"],
                item_dict["stat_change_list"]
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
        else:
            item = inventory.Item(
                item_dict["name"],
                item_dict["description"],
                item_dict["amount"],
                item_dict["individual_value"],
                item_dict["object_type"]
            )
        player.inventory.items.append(item)
    
    # 恢复装备
    for slot, equip_dict in player_dict["equipment"].items():
        if equip_dict:
            equipment = inventory.Equipment(
                equip_dict["name"],
                equip_dict["description"],
                equip_dict["amount"],
                equip_dict["individual_value"],
                equip_dict["object_type"],
                equip_dict["stat_change_list"]
            )
            player.equipment[slot] = equipment
    
    # 恢复咒语（参考预定义咒语）
    spell_mapping = {
        "火球术": skills.fire_ball,
        "神圣祝福": skills.divineBlessing,
        "班尼特的奇妙旅程": skills.benettFantasticVoyage
    }
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

def delete_save(save_name):
    """删除存档"""
    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.json")

    if os.path.exists(save_path):
        os.remove(save_path)
        return True
    return False