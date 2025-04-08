import json
import os
import time
import pickle

from player import Player

SAVE_FOLDER = "saves"

def ensure_save_folder():
    """确保存档文件夹存在"""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def save_game(player, save_name=None):
    """保存游戏进度"""
    ensure_save_folder()

    if not save_name:
        save_name = f"save_{int(time.time())}"

    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.sav")

    save_metadata = {
        "name": save_name,
        "player_name": player.name,
        "level": player.level,
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(os.path.join(SAVE_FOLDER, f"{save_name}.meta"), "w") as meta_file:
        json.dump(save_metadata, meta_file)

    with open(save_path, "wb") as save_file:
        pickle.dump(player, save_file)

    return save_metadata

def load_game(save_name):
    """加载游戏存档"""
    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.sav")
    if not os.path.exists(save_path):
        print(f"存档 '{save_name}' 不存在")
        return None
    try:
        with open(save_path, "rb") as save_file:
            player = pickle.load(save_file)
        return player
    except Exception as e:
        print(f"加载存档失败: {e}")
        return None

def get_save_list():
    """获取所有存档列表"""
    ensure_save_folder()
    saves = []
    for filename in os.listdir(SAVE_FOLDER):
        if filename.endswith(".meta"):
            save_name = filename[:-5]
            with open(os.path.join(SAVE_FOLDER, filename), "r") as meta_file:
                metadata = json.load(meta_file)
                saves.append(metadata)

    saves.sort(key=lambda x: x["timestamp"], reverse=True)
    return saves

def delete_save(save_name):
    """删除存档"""
    meta_path = os.path.join(SAVE_FOLDER, f"{save_name}.meta")
    save_path = os.path.join(SAVE_FOLDER, f"{save_name}.sav")

    if os.path.exists(meta_path):
        os.remove(meta_path)

    if os.path.exists(save_path):
        os.remove(save_path)
        return True
    return False
