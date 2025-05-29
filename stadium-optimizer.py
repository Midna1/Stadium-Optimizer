import streamlit as st
from itertools import combinations

# --- Item class ---
class Item:
    def __init__(self, name, stats, cost, category, character=None):
        self.name = name
        self.stats = stats
        self.cost = cost
        self.category = category
        self.character = character

# --- Item pool ---
ITEM_POOL = [
    Item("Power Playbook", {"Ability Power": 0.10}, 1000, "Ability"),
    Item("Charged Plating", {"Armor": 25, "Ability Power": 0.10}, 1000, "Ability"),
    Item("Shady Spectacles", {"Ability Lifesteal": 0.10}, 1000, "Ability"),
    Item("Winning Attitude", {"HP": 25}, 1500, "Ability"),
    Item("Custom Stock", {"Weapon Power": 0.05, "Ability Power": 0.10}, 3750, "Ability"),
    Item("Biolight Overflow", {"HP": 25, "Ability Power": 0.05}, 4000, "Ability"),
    Item("Energized Bracers", {"Ability Power": 0.10, "Ability Lifesteal": 0.10}, 4000, "Ability"),
    Item("Junker Whatchamajig", {}, 4000, "Ability"),
    Item("Wrist Wraps", {"Ability Power": 0.05, "Attack Speed": 0.10}, 4000, "Ability"),
    Item("Multi-Tool", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, 4500, "Ability"),
    Item("Nano-Cola", {"Ability Power": 0.20}, 6000, "Ability"),
    Item("Three-Tap Tommygun", {"Ability Power": 0.10, "Attack Speed": 0.10}, 9500, "Ability"),
    Item("Biotech Maximizer", {"HP": 25, "Ability Power": 0.10}, 10000, "Ability"),
    Item("Catalytic Crystal", {"Ability Power": 0.15}, 10000, "Ability"),
    Item("Lumerico Fusion Drive", {"Armor": 50, "Ability Power": 0.15}, 10000, "Ability"),
    Item("Superflexor", {"HP": 25, "Weapon Power": 0.10, "Ability Power": 0.25}, 10000, "Ability"),
    Item("Cybervenom", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, 10500, "Ability"),
    Item("Iridescent Iris", {"Ability Power": 0.20, "Cooldown Reduction": 0.10}, 11000, "Ability"),
    Item("Liquid Nitrogen", {"HP": 25, "Ability Power": 0.10}, 11000, "Ability"),
    Item("Mark of the Kitsune", {"Ability Power": 0.10}, 11000, "Ability"),
    Item("Champion's Kit", {"Ability Power": 0.40}, 13500, "Ability"),
]

# --- Base character stats ---
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# --- Optimization targets ---
target_relevant_stats = {
    "HP": {"HP"},
    "Shields": {"Shields"},
    "Armor": {"Armor"},
    "Damage Reduction": {"Damage Reduction"},
    "Total HP": {"HP", "Shields", "Armor"},
    "Weapon Power": {"Weapon Power"},
    "Ability Power": {"Ability Power", "Cooldown Reduction"},
    "Attack Speed": {"Attack Speed"},
    "Cooldown Reduction": {"Cooldown Reduction", "Ability Power"},
    "Max Ammo": {"Max Ammo"},
    "Weapon Lifesteal": {"Weapon Lifesteal"},
    "Ability Lifesteal": {"Ability Lifesteal"},
    "Move Speed": {"Move Speed"},
    "Reload Speed": {"Reload Speed"},
    "Melee Damage": {"Melee Damage"},
    "Critical Hit Damage": {"Critical Hit Damage"},
    "Effective HP": {"HP", "Shields", "Armor", "Damage Reduction"},
    "Weapon DPS": {"Weapon Power", "Attack Speed", "Reload Speed", "Critical Hit Damage"},
    "Ability DPS": {"Ability Power", "Cooldown Reduction"},
}

# --- Functions ---
def filter_items_for_target(items, target):
    relevant = target_relevant_stats.get(target, set())
    return [item for item in items if any(stat in relevant for stat in item.stats)]

def calculate_build_stats(items, base):
    stats = {
        "HP": base.get("HP", 0),
        "Shields": base.get("Shields", 0),
        "Armor": base.get("Armor", 0),
        "Weapon Power": 0.0,
        "Ability Power": 0.0,
        "Attack Speed": 0.0,
        "Reload Speed": 0.0,
        "Cooldown Reduction": 1.0,
        "Damage Reduction": 0.0,
        "Weapon Lifesteal": 0.0,
        "Ability Lifesteal": 0.0,
        "Move Speed": 0.0,
        "Melee Damage": 0.0,
        "Critical Hit Damage": 0.0,
        "Max Ammo": 0,
    }
    for item in items:
        for stat, val in item.stats.items():
            if stat == "Cooldown Reduction":
                stats["Cooldown Reduction"] *= (1 - val)
            elif stat in stats:
                stats[stat] += val
    stats["Cooldown Reduction"] = max(stats["Cooldown Reduction"], 0.1)
    stats["Ability Power"] *= stats["Cooldown Reduction"]
    return stats

def evaluate_build(stats, target):
    if target == "Effective HP":
        total = stats["HP"] + stats["Shields"] + stats["Armor"]
        return total / max(0.01, 1 - min(stats["Damage Reduction"], 0.99))
    if target == "Total HP":
        return stats["HP"] + stats["Shields"] + stats["Armor"]
    if target == "Cooldown Reduction":
        return 1 - stats["Ability Power"]
    if target == "Ability DPS":
        base_dps = 80
        return base_dps * (1 + stats["Ability Power"]) * (1 / stats["Cooldown Reduction"])
    if target == "Weapon DPS":
        base_dps = 100
        return base_dps * (1 + stats["Weapon Power"]) * (1 + stats["Attack Speed"]) * (1 + stats["Reload Speed"]) * (1 + stats["Critical Hit Damage"])
    return stats.get(target, 0)

def display_relevant_stats(stats, target):
    relevant = target_relevant_stats.get(target, set())
    lines = []
    for base_stat in ["HP", "Shields", "Armor"]:
        if base_stat in relevant or target in ["Total HP", "Effective HP"]:
            lines.append(f"{base_stat}: {stats.get(base_stat, 0)}")
    for stat in relevant:
        if stat in ["HP", "Shields", "Armor"]:
            continue
        val = stats.get(stat, 0)
        if isinstance(val, float) and abs(val) < 10:
            lines.append(f"{stat}: {val * 100:.1f}%")
        else:
            lines.append(f"{stat}: {val}")
    return lines

# --- Streamlit UI ---
st.title("Build Optimizer")

character = st.selectbox("Character", list(BASE_STATS.keys()))
max_cost = st.number_input("Max Budget", 0, 500000, 10000, 100)
target = st.selectbox("Optimization Target", list(target_relevant_stats.keys()))

filtered_items = filter_items_for_target(
    [i for i in ITEM_POOL if i.character is None or i.character == character],
    target
)

best_score = float("-inf")
best_build = None

for r in range(1, 7):  # Up to 6 items
    for combo in combinations(filtered_items, r):
        cost = sum(i.cost for i in combo)
        if cost > max_cost:
            continue
        stats = calculate_build_stats(combo, BASE_STATS[character])
        score = evaluate_build(stats, target)
        if score > best_score:
            best_score = score
            best_build = combo

if best_build:
    st.subheader("Best Build")
    st.write("Items:")
    for item in best_build:
        st.markdown(f"- {item.name}")
    st.write(f"Total Cost: {sum(i.cost for i in best_build)}")
    st.subheader("Key Stats")
    for line in display_relevant_stats(calculate_build_stats(best_build, BASE_STATS[character]), target):
        st.write(line)
    st.write(f"Score ({target}): {best_score:.3f}")
else:
    st.write("No valid build found.")
