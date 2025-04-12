import csv
import os

CSV_FILE = "data/extended_enemies.csv"

FIELDNAMES = [
    "id", "name", "name_zh", "max_hp", "max_mp",
    "atk", "def", "mat", "mdf", "agi", "luk", "crit",
    "xp_reward", "gold_min", "gold_max"
]

def get_monster_input():
    print("\n请输入怪物数据:")
    monster = {}
    for field in FIELDNAMES:
        value = input(f"{field}: ")
        monster[field] = value
    return monster

def save_to_csv(monster_data, filename=CSV_FILE):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(monster_data)
    print(f"✅ 怪物 {monster_data['name_zh']} 已保存到 {filename}。")

def main():
    while True:
        monster = get_monster_input()
        save_to_csv(monster)
        cont = input("是否继续添加怪物？(y/n): ").strip().lower()
        if cont != "y":
            break

if __name__ == "__main__":
    main()
