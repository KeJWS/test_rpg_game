from csv_diff import load_csv, compare
import json

with open("data/enemies.csv", encoding="utf-8") as old_file, open("data/monsters.csv", encoding="utf-8") as new_file:
    diff = compare(
        load_csv(old_file, key="id"),
        load_csv(new_file, key="id")
    )

print(json.dumps(diff, indent=2, ensure_ascii=False))

with open('data/diff_enemies.json', 'w', encoding='utf-8') as json_file:
    json.dump(diff, json_file, ensure_ascii=False, indent=4)

print("数据已保存为 diff.json")