command_docs = {
    "p": """
p 玩家相关命令:
  --help    查看玩家指令帮助
  -hp       显示玩家当前血量
  -mp       显示玩家当前魔法值
  -gold     显示玩家当前金币
  -lr       生命恢复水晶(life_recovery_crystal)
  -se       查看玩家装备(show_equipment_info)
  -sk       查看玩家技能(show_skills)
  -stats    显示玩家详细数据(debug_show_stats)
  -heal     恢复全部生命值(fully_heal)[debug]
  -mana     恢复全部魔法值(fully_recover_mp)[debug]
  -bag      查看背包[debug]
  -level n  升级到n[debug]
""",
    "p.i": """
p.i 玩家背包相关命令:
  --help        查看背包指令帮助
  -U            使用物品(use_item)
  -D            丢弃物品(drop_item)
  -E            装备物品(equip_item)
  -C            比较装备(compare_equipment)
  -ua           卸下全部装备(unequip_all)
  -vi           查看物品详情(view_item_detail)
  -show         查看背包物品(show_inventory_item)
  -sort         整理背包物品
  -count        统计背包物品数量
  --give-all    全物品[debug]
  -spawn        刷出指定物品 (用法: p.i -spawn item_name quantity)
""",
    "a.d": """
a.d 攻防相关命令
  -db enemy     显示玩家和 enemy 的对比信息(display_battle_stats)
""",
    "p.gold": "p.gold amount    刷 amount 数量金币[debug]",
    "p.exp": "p.exp amount    刷 amount 数量经验[debug]",
    "p.ap": "p.ap amount    刷 amount 数量能力点[debug]",
    "jack.i": """
jack 商店相关命令(其他商店类似)
    jack.i -buy    购买物品[debug]
""",
    "default": "可用主题: p, p.i\n例如: p --help",
}
