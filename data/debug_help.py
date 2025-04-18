command_docs = {
    "p": """
p 玩家相关命令:
  --help    查看玩家指令帮助
  -hp       显示玩家当前血量
  -mp       显示玩家当前魔法值
  -gold     显示玩家当前金币
  -lr       生命恢复水晶
  -se       查看玩家装备
  -sk       查看玩家技能
  -stats    显示玩家详细数据
  -heal     恢复全部生命值[debug]
  -mana     恢复全部魔法值[debug]
  -bag      查看背包[debug]
  -level n  升级到n[debug]
""",
    "p.i": """
p.i 玩家背包相关命令:
  --help        查看背包指令帮助
  -U            使用物品
  -D            丢弃物品
  -E            装备物品
  -C            比较装备
  -ua           卸下全部装备
  -vi           查看物品详情
  -si           查看背包物品
  --give-all    全物品[debug]
  -spawn       刷出指定物品 (用法: p.i -spawn item_name quantity)
""",
    "p.gold": "p.gold amount    刷 amount 数量金币[debug]",
    "p.exp": "p.exp amount    刷 amount 数量经验[debug]",
    "jack.i": """
jack 商店相关命令(其他商店类似)
    jack.i --buy    购买物品[debug]
""",
    "default": "可用主题: p\n例如: p --help",
}
