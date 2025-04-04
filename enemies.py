import data

class Imp(data.Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 1000,
            "hp": 1000,
            "max_mp": 10,
            "mp": 10,
            "atk": 15,
            "def": 10,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10,
            "crit": 10
        }
        xp_reward = 40
        super().__init__("小鬼", stats, xp_reward)

class Golem(data.Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 1500,
            "hp": 1500,
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
