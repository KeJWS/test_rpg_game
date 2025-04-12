def exp_required(level, formula):
    if level == 1:
        return 0
    return int(formula(level))

def exp_required_formula_1(level):
    base = 100
    growth = (level ** 2.4) * 1.2
    scaling = level * 35
    return base + growth + scaling

def exp_required_formula_1_5(level):
    base = 100 * level
    growth = (level ** 2.5) * 1.25
    scaling = level * 35
    return base + growth + scaling

def exp_required_formula_2(level):
    return 100 * (level ** 2.75) + level * 40

def exp_required_formula_3(level):
    return 50 * 1.5**(level - 1)

def exp_required_formula_4(level):
    return 35 * 1.5**(level - 1) + 10 * level * level

def exp_required_formula_5(level):
    return 100 * 1.2**(level - 1) + 10 * level * level

def exp_table(max_level=100, formula=None):
    table = []
    total = 0
    for lvl in range(1, max_level + 1):
        need = exp_required(lvl, formula)
        total += need
        table.append((lvl, f"{need:G}", f"{total:G}"))
    return table

if __name__ == "__main__":
    formulas = [
        exp_required_formula_1,
        exp_required_formula_1_5,
    ]

    for i, formula in enumerate(formulas, start=1):
        print(exp_table(formula=formula))
        print()