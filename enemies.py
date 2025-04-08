# 修改 enemies.py，添加AI能力
import combat
import random
import skills

class Enemy(combat.Battler):
    def __init__(self, name, stats, xp_reward) -> None:
        super().__init__(name, stats)
        self.xp_reward = xp_reward
        self.abilities = []  # 可用技能列表
        self.ai_type = "aggressive"  # 默认AI类型
    
    def choose_action(self, player, enemies):
        """AI决策逻辑"""
        if self.ai_type == "aggressive":
            return self.aggressive_ai(player, enemies)
        elif self.ai_type == "defensive":
            return self.defensive_ai(player, enemies)
        elif self.ai_type == "support":
            return self.support_ai(player, enemies)
        else:
            return {"action": "attack", "target": player}
    
    def aggressive_ai(self, player, enemies):
        """攻击型AI行为"""
        # 如果HP低于30%，有25%几率使用回复技能（如果有）
        if self.stats["hp"] < self.stats["max_hp"] * 0.3 and random.random() < 0.25:
            for ability in self.abilities:
                if isinstance(ability, skills.Simple_heal_spell):
                    return {"action": "ability", "ability": ability, "target": self}
        
        # 如果有攻击技能且MP足够，60%几率使用
        attack_abilities = [a for a in self.abilities 
                           if isinstance(a, skills.Simple_offensive_spell) 
                           and self.stats["mp"] >= a.mp_cost]
        
        if attack_abilities and random.random() < 0.6:
            chosen_ability = random.choice(attack_abilities)
            return {"action": "ability", "ability": chosen_ability, "target": player}
        
        # 默认使用普通攻击
        return {"action": "attack", "target": player}
    
    def defensive_ai(self, player, enemies):
        """防御型AI行为"""
        # 如果HP低于50%，有70%几率使用防御
        if self.stats["hp"] < self.stats["max_hp"] * 0.5 and random.random() < 0.7:
            return {"action": "defend"}
            
        # 如果HP低于30%，有高几率使用治疗（如果有）
        if self.stats["hp"] < self.stats["max_hp"] * 0.3 and random.random() < 0.8:
            for ability in self.abilities:
                if isinstance(ability, skills.Simple_heal_spell):
                    return {"action": "ability", "ability": ability, "target": self}
        
        # 默认使用普通攻击
        return {"action": "attack", "target": player}
    
    def support_ai(self, player, enemies):
        """辅助型AI行为"""
        # 寻找血量最低的友方单位
        lowest_hp_ally = None
        lowest_hp_percentage = 1.0
        
        for ally in enemies:
            if ally == self:
                continue
                
            hp_percentage = ally.stats["hp"] / ally.stats["max_hp"]
            if hp_percentage < lowest_hp_percentage:
                lowest_hp_percentage = hp_percentage
                lowest_hp_ally = ally
        
        # 如果有友方单位HP低于50%，尝试使用治疗技能
        if lowest_hp_ally and lowest_hp_percentage < 0.5:
            for ability in self.abilities:
                if isinstance(ability, skills.Simple_heal_spell):
                    return {"action": "ability", "ability": ability, "target": lowest_hp_ally}
        
        # 尝试使用增益技能
        buff_abilities = [a for a in self.abilities 
                         if isinstance(a, skills.Buff_debuff_spell) 
                         and self.stats["mp"] >= a.mp_cost]
        
        if buff_abilities and random.random() < 0.7:
            chosen_ability = random.choice(buff_abilities)
            # 如果是增益技能，给友方；如果是减益技能，给敌人
            if chosen_ability.amount_to_change > 0:
                target = random.choice(enemies)
            else:
                target = player
            return {"action": "ability", "ability": chosen_ability, "target": target}
        
        # 默认使用普通攻击
        return {"action": "attack", "target": player}

# 为现有怪物添加技能和AI类型
class Imp(Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 500,
            "hp": 500,
            "max_mp": 100,
            "mp": 100,
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
        # 添加技能
        self.abilities = [skills.fire_ball]
        self.ai_type = "aggressive"

class Golem(Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 1000,
            "hp": 1000,
            "max_mp": 50,
            "mp": 50,
            "atk": 20,
            "def": 20,
            "mat": 10,
            "mdf": 10,
            "agi": 5,
            "luk": 10,
            "crit": 0
        }
        xp_reward = 100
        super().__init__("魔像", stats, xp_reward)
        
        # 创建石肤技能 (减伤buff)
        stone_skin = skills.Buff_debuff_spell(
            "石肤", "增加防御力", 0, 20, "def", 0.3, 3
        )
        self.abilities = [stone_skin]
        self.ai_type = "defensive"

class Giant_slime(Enemy):
    def __init__(self) -> None:
        stats = {
            "max_hp": 2000,
            "hp": 2000,
            "max_mp": 150,
            "mp": 150,
            "atk": 15,
            "def": 15,
            "mat": 10,
            "mdf": 10,
            "agi": 10,
            "luk": 10,
            "crit": 0
        }
        super().__init__("巨型史莱姆", stats, 200)
        
        # 创建分裂技能
        acid_splash = skills.Simple_offensive_spell("酸液飞溅", "对敌人造成伤害", 60, 25)
        healing_jelly = skills.Simple_heal_spell("治疗黏液", "回复生命值", 75, 30)
        
        self.abilities = [acid_splash, healing_jelly]
        self.ai_type = "support"