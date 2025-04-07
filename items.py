import inventory

# 基本物品
long_sword = inventory.Equipment('长剑', '', 1, 20, 'weapon', {'atk' : 6})
dagger = inventory.Equipment('匕首', '', 1, 15, 'weapon', {'atk' : 3, 'crit' : 10, 'agi': 3})
staff = inventory.Equipment('棍棒', '', 1, 18, 'weapon', {'mat' : 3, 'max_mp' : 2})

cloth_armor = inventory.Equipment('布甲', '', 1, 10, 'wrmor', {'max_hp' : 2, 'def' : 2})

# 高级物品
war_hammer = inventory.Equipment('战锤', '', 1, 62, 'weapon', {'atk' : 13, 'agi' : -2})
iron_armor = inventory.Equipment('铁甲', '', 1, 102, 'armor', {'max_hp' : 8, 'def' : 10})

# 消耗品
hp_potions = inventory.Potion('生命药水', 'a', 4, 10, 'consumable', 'hp', 15)
mp_potions = inventory.Potion('法力药水', 'a', 4, 10, 'consumable', 'mp', 15)
