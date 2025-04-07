import combat

class Imp(combat.Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 500,
            "hp": 500,
            "max_mp": 10,
            "mp": 10,
            "atk": 15,
            "def": 10,
            "mat": 10,
            "mdf": 10,
            "agi": 9,
            "luk": 10,
            "crit": 5
        }
        xp_reward = 40
        super().__init__("小鬼", stats, xp_reward)

class Golem(combat.Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 1000,
            "hp": 1000,
            "max_mp": 10,
            "mp": 10,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10,
            "crit": 0
        }
        xp_reward = 100
        super().__init__("魔像", stats, xp_reward)

class Giant_slime(combat.Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 2000,
            "hp": 2000,
            "max_mp": 10,
            "mp": 10,
            "atk": 15,
            "def": 15,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10,
            "crit": 0
        }
        super().__init__("巨型史莱姆", stats, 20)
