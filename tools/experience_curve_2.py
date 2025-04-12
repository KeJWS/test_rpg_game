import matplotlib.pyplot as plt

# Optimized experience functions in a dictionary for clean iteration
def exp_required_1(level):
    if level == 1:
        return 0
    return int(100 + (level ** 2.4) * 1.2 + level * 35)

def exp_required_1_5(level):
    if level == 1:
        return 0
    return int(100 * level + (level ** 2.5) * 1.25 + level * 35)

def exp_required_2(level):
    if level == 1:
        return 0
    return int(100 * (level ** 2.75) + level * 40)

def exp_required_3(level):
    if level == 1:
        return 0
    return int(50 * 1.5 ** (level - 1))

def exp_required_4(level):
    if level == 1:
        return 0
    return int(35 * 1.5 ** (level - 1) + 10 * level * level)

def exp_required_5(level):
    if level == 1:
        return 0
    return int(100 * 1.2 ** (level - 1) + 10 * level * level)

exp_functions = {
    "exp_required_1": exp_required_1,
    "exp_required_1_5": exp_required_1_5,
}

# Generate data
max_level = 1000
levels = list(range(1, max_level + 1))
exp_data = {}

for name, func in exp_functions.items():
    total = 0
    per_level_exp = []
    total_exp = []
    for lvl in levels:
        need = func(lvl)
        total += need
        per_level_exp.append(need)
        total_exp.append(total)
    exp_data[name] = {
        "per_level": per_level_exp,
        "total": total_exp
    }

# Plotting
plt.figure(figsize=(14, 6))

# Per-level EXP
plt.subplot(1, 2, 1)
for name, data in exp_data.items():
    plt.plot(levels, data["per_level"], label=name)
plt.title("EXP Required per Level")
plt.xlabel("Level")
plt.ylabel("EXP to Next Level")
plt.legend()
plt.grid(True)

# Total EXP
plt.subplot(1, 2, 2)
for name, data in exp_data.items():
    plt.plot(levels, data["total"], label=name)
plt.title("Total Cumulative EXP")
plt.xlabel("Level")
plt.ylabel("Total EXP")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
