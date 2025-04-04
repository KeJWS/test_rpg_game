import data

class Imp(data.Enemy):

    def __init__(self) -> None:
        stats = {
            "hp": 200,
            "mp": 10,
            "atk": 15,
            "def": 10,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "crit": 10
        }
        xp_reward = 40
        super().__init__("Imp", stats, xp_reward)
