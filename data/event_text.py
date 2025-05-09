from rich.panel import Panel
from rich.text import Text

# 初始事件
def initial_event_text():
    pannel = Panel.fit(
        Text(
            "\n这一天终于到来了。你已在冒险者公会登记了自己的姓名。\n"
            "作为礼物，他们允许你从以下装备中选择一套。你会选择哪一套？\n\n"
            "   1 - 战士 - 擅长近战攻击和防御 (默认)\n"
            "   2 - 盗贼 - 敏捷高，擅长快速打击\n"
            "   3 - 法师 - 强大的法术攻击能力\n"
            "   4. 弓箭手 - 远程物理攻击专家\n"
            "   5. 圣骑士 - 兼顾攻防与治愈魔法\n"
            "   6. 死灵法师 - 操纵亡灵的黑暗施法者\n"
        ),
        title="KWT RPG Game",
        subtitle="welcome",
        border_style="bold green",
    )
    return pannel

# 安全镇
# *安娜的防具店
anna_armor_shop_encounter = "在一个古老的城镇中，你发现自己站在一家店铺前。\n\
门上挂着一块招牌，上面写着：<安娜的防具店>。\n\
要进入吗？[y/n]"
anna_armor_shop_enter = "“欢迎，冒险者！我这里有各种防具供你选择。”一位温柔的女子说道。\n"
anna_armor_shop_talk = "“我提供从轻甲到重甲的各种装备，适合不同的冒险者。”安娜微笑着说。\n\
“来看看吧，也许你能找到心仪的防具。”\n"
anna_armor_shop_exit = "你离开了防具店，继续你的冒险旅程。\n"

# *杰克的武器店
jack_weapon_shop_encounter = "在一个繁忙的市集上，你发现自己站在一家店铺前。\n\
门上挂着一块招牌，上面写着：<杰克的武器店>。\n\
要进入吗？[y/n]"
jack_weapon_shop_enter = "“欢迎光临，勇敢的战士！需要什么武器吗？”一个面带微笑的男子问道。\n"
jack_weapon_shop_talk = "“我这里有各种武器，从锋利的剑到强大的弓箭。”杰克自豪地说。\n\
“你可以看看这些武器，也许能找到适合你的。”\n"
jack_weapon_shop_exit = "你离开了武器店，继续你的冒险旅程。\n"

# *玛丽的小吃摊
mary_food_stall_encounter = "在镇中心的小广场，你看见一位热情的大妈在一辆小推车旁招呼客人。\n\
招牌上写着：<玛丽的小吃摊>。\n\
你要停下来看看她卖什么吗？[y/n]"
mary_food_stall_enter = "“来尝尝我家的点心吧！”玛丽笑着说道，热腾腾的香味扑面而来。\n"
mary_food_stall_talk = "“我做的烤肉和蜂蜜苹果最受冒险者欢迎啦。”玛丽骄傲地说。\n"
mary_food_stall_exit = "你告别玛丽，继续踏上旅程，肚子还带着点满足感。\n"

# 龙脊山
# *里克的盔甲店
rik_armor_shop_encounter = "在一个小村庄四处游荡时，你发现自己站在一家店铺前。\n\
门上挂着一块招牌，上面写着：<里克的护甲店>。\n\
要进入吗？[y/n]"
rik_armor_shop_enter = "“你好，朋友！你需要点什么？” 一个身材魁梧的男子问道。\n"
rik_armor_shop_talk = "“我这里有各种护甲，适合不同的战士。” 里克笑着说。\n"
rik_armor_shop_exit = "你离开了村庄，继续踏上冒险之旅。\n"

# *青铜匠
lok_armor_shop_encounter = "<里克的护甲店> 旁边便是他徒弟: 青铜匠的住所了。\n\
你的到来没有影响到丝毫, 他依旧专心的做着手中的活。\n\
门没关, 进来吧...[y/n]"
lok_armor_shop_enter = "利剑还是青铜盾？\n"
lok_armor_shop_talk = "我做的东西，也许能帮你在山里多活几分钟。\n"
lok_armor_shop_exit = "祝你好运...\n"

# 迷雾沼泽
# *伊兹的魔法店
itz_magic_encounter = "你误入了一片沼泽。环顾四周，你发现一座小屋。\n\
门上挂着一块招牌，上面写着：<伊兹的魔法店>。\n\
要进入吗？[y/n]"
itz_magic_enter = "屋内站着一位戴着厚重眼镜的矮小女子，她看上去像是一位女巫。\n\
她低声呢喃道：“哦？看看是谁来了……来吧，随意看看！”\n"
itz_magic_talk = "“嗯，我能感觉到你身上有一些特殊的气息。” 伊兹微微抬起头，眯眼看着你。\n\
“这里有各式各样的法术书，草药，还有一些你可能需要的魔法物品。” 她指向架子上堆满了书籍和瓶瓶罐罐的地方。\n"
itz_magic_exit = "你离开了沼泽，继续踏上旅程。\n"

# *贝鲁格锻造屋
belrug_encounter = "你在一处冒着热气的山坡上发现了一间矮小的石屋，火光映红了屋顶。\n\
招牌上写着：<贝鲁格锻造屋>。\n\
要进入吗？[y/n]"
belrug_enter = "“哎哟，是个新面孔啊！” 屋内传来锤子落下的声音，一个满脸胡茬的壮汉露出笑容。\n\
“想找点真正能砸出火星的好家伙吗？”"
belrug_talk = "“我这儿的每件武器都是我亲手打的，用的都是黑曜矿。你要是能帮我弄到更多，我就能做出更厉害的东西。”"
belrug_quest = "贝鲁格：听说东边矿坑有些黑曜矿石，你要是能弄来几块，我给你打一把独一无二的阔剑！"
belrug_exit = "你告别了铁匠，火光在他背后依旧明亮。"

# *米拉的小屋
mira_encounter = "你穿过密林，迷失在一片阴影中。\n\
远处出现了一间隐秘的小屋，上面挂着鹿角和干草圈。\n\
要靠近看看吗？[y/n]"
mira_enter = "门被轻轻推开，一位身材纤细、目光锐利的女子端着弓箭站在屋内。\n\
“你不是野兽......进来吧。”"
mira_talk = "“我这里有一些你在城市找不到的东西——专为猎人和游击者打造。” 她边说边检查弓弦。"
mira_exit = "你离开小屋，树影在你背后轻轻晃动。"

# *索雷恩的魔术工坊
soren_encounter = "你来到一座被藤蔓缠绕的古老塔楼，入口处闪烁着符文光芒。\n\
一块悬浮的石板写着：<索雷恩的魔术工坊>。\n\
是否进入？[y/n]"
soren_enter = "一个身披披风的男子站在魔法阵中，背对着你。\n\
“哦，又一位追寻力量的旅者……进来吧。”"
soren_talk = "“我的收藏中，有些东西并不适合凡人。但你若能带来魔导刻印，也许我会为你破例。”"
soren_quest = "索雷恩：这片大陆隐藏着七个魔导刻印，每一个都有不同的源力……带它们来，我便可为你附魔古物。"
soren_exit = "你转身离开，塔楼的门无声关闭，仿佛从未存在。"

# *神秘商人
mysterious_businessman_encounter = "\n我这儿应该有你需要的...是否进入? [y/n]"
mysterious_businessman_enter = "你好...\n"
mysterious_businessman_talk = "...\n"
mysterious_businessman_exit = "你离开了，继续踏上旅程。\n"

## 治疗

# *美杜莎神像
medussa_statue_encounter = "在一座山丘的顶端，你发现了一座小型神殿。\n\
这里矗立着一尊古老而被遗忘的女神雕像。\n\
不知为何，你心生敬意，想要向它致敬。\n\
是否跪拜？[y/n]"
medussa_statue_success = "你感受到一股温暖的力量流遍全身。\n"
medussa_statue_fail = "什么也没有发生，或许只是你的错觉。\n"
medussa_statue_refuse = "你决定不跪拜。\n"

# *客栈事件
inn_event_encounter = "在穿越森林的途中，你发现了一家客栈。\n\
你可以在这里休息，但需要支付一定的费用。\n\
支付 20G 住一晚吗？[y/n]"
inn_event_success = "你在柔软舒适的床上安然入睡。\n"
inn_event_fail = "你的钱不够。\n"
inn_event_refuse = "你决定不支付住宿费。\n"

## 任务
# 龙脊山
quest_caesarus_bandit_text = "凯撒鲁斯和他的匪徒一直在\n\
骚扰附近的村庄。去解决他们吧。"
shop_quest_caesarus_bandits = "里克: 听说过那群强盗吗？他们一直在恐吓\n\
这一带的村庄。一个叫凯撒鲁斯的家伙是他们的首领。\n\
如果你能解决他们，也许村民会给你一些报酬。"

# 雾林
quest_fight_against_slime_text = "你已经准备好去消灭那些史莱姆了。"
shop_fight_against_slime_text = "安全镇镇长: 可恨的史莱姆给这个镇子带来了不少的破坏，\n\
希望英雄你可以出手相助将其彻底解决。"

quest_fight_against_slime_king_text = "沼泽深处出现了一只巨大的史莱姆之王，\n\
你接下了这个任务。"
shop_fight_against_slime_king_text = "魔法师伊兹: 听闻沼泽深处出现了一只巨大的史莱姆之王，\n\
有兴趣吗？报酬嘛，我倒是可以把珍藏多年的长弓送给你..."

# 迷雾沼泽
quest_fight_against_wolf_king_text = ""
shop_fight_against_wolf_king_text = "米拉：最近森林深处来了头夜行狼王，它已经吞了不少旅人。\n\
如果你有胆子，可以帮我除掉它。"

# 通用事件
find_coins_text = "真幸运! 你在地上发现了一些零钱!"
admire_scenery_text = "你欣赏了美丽的景色, 获得了少量经验"
friendly_villager_text = "村民提供给了你一些金币, 食物"
find_herb_text = "你找到了一些认识的草药, 然后使用了"
rest_spot_text = "你在一个安静的地方短暂休息"
