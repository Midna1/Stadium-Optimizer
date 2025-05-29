import streamlit as st
from itertools import combinations

# --- Item class with extra_effect support ---
class Item:
    def __init__(self, name, stats, cost, category, character=None, extra_effect=None):
        self.name = name
        self.stats = stats
        self.cost = cost
        self.category = category
        self.character = character
        self.extra_effect = extra_effect

# --- Pulsar Torpedos effect function ---
def pulsar_torpedos_effect(stats, base_value=20):
    ability_power = stats.get("Ability Power", 0.0)
    return base_value * (1 + ability_power)
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
    Item("Champion's Kit", {"Ability Power": 0.40}, 14000, "Ability"),

    #Juno Exclusive
    Item("Lock-On Shield", {"Ability Power": 0.1001}, cost=4000, category="Ability", character="Juno"),
    Item("Lux Loop", {"Ability Power": 0.1001}, cost=4000, category="Ability", character="Juno"),
    Item("Pulsar Torpedos", {"Ability Lifesteal": 0.10}, 10000, "Ability", character="Juno", extra_effect=pulsar_torpedos_effect),
    Item("Solar Shielding", {"Ability Power": 0.15}, cost=10000, category="Ability", character="Juno"),
    Item("Red Promise Regulator", {"Shields": 50, "Ability Power": 0.15}, cost=10000, category="Ability", character="Juno"),

    
]

# --- Base stats ---
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# --- Optimization target stat map ---
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
    "Ability DPS": {"Ability Power", "Cooldown Reduction", "Ability Lifesteal"},
}

# --- Helper functions ---
def filter_items_for_target(items, target):
    relevant_stats = target_relevant_stats.get(target, set())
    return [
        item for item in items
        if any(stat in relevant_stats for stat in item.stats.keys()) or item.extra_effect
    ]

def calculate_build_stats(items, base_stats):
    stats = {
        "HP": base_stats.get("HP", 0),
        "Shields": base_stats.get("Shields", 0),
        "Armor": base_stats.get("Armor", 0),
        "Max Ammo": 0,
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
    }

    for item in items:
        for stat, val in item.stats.items():
            if stat == "Cooldown Reduction":
                stats["Cooldown Reduction"] *= (1 - val)
            elif stat in stats:
                stats[stat] += val
            else:
                stats[stat] = val

    if stats["Cooldown Reduction"] < 0.1:
        stats["Cooldown Reduction"] = 0.1

    stats["Ability Power"] *= stats["Cooldown Reduction"]
    return stats

def evaluate_build(stats, target, items):
    if target == "Ability DPS":
        base_ability_dps = 80
        ability_power = 1 + stats.get("Ability Power", 0)
        cooldown_mult = stats.get("Cooldown Reduction", 1.0)
        ability_lifesteal = 1 + stats.get("Ability Lifesteal", 0)

        bonus_damage = sum(item.extra_effect(stats) for item in items if item.extra_effect)
        return (base_ability_dps + bonus_damage) * ability_power * (1 / cooldown_mult) * ability_lifesteal

    if target == "Effective HP":
        total_hp = stats["HP"] + stats["Shields"] + stats["Armor"]
        dmg_red = stats.get("Damage Reduction", 0)
        return total_hp / (1 - min(dmg_red, 0.99))

    if target == "Weapon DPS":
        base_dps = 100
        return base_dps * (1 + stats["Weapon Power"]) * (1 + stats["Attack Speed"]) * (1 + stats["Reload Speed"]) * (1 + stats["Critical Hit Damage"])

    if target == "Cooldown Reduction":
        return 1 - stats["Ability Power"]

    if target in stats:
        return stats[target]
    if target == "Total HP":
        return stats["HP"] + stats["Shields"] + stats["Armor"]
    return 0

def display_relevant_stats(stats, target):
    relevant_stats = target_relevant_stats.get(target, set())
    lines = []
    for base in ["HP", "Shields", "Armor"]:
        if base in relevant_stats or target in ["Total HP", "Effective HP"]:
            lines.append(f"{base}: {stats[base]}")

    for stat in relevant_stats:
        if stat in ["HP", "Shields", "Armor"]:
            continue
        val = stats.get(stat)
        if isinstance(val, float) and abs(val) < 10:
            lines.append(f"{stat}: {val * 100:.1f}%")
        else:
            lines.append(f"{stat}: {val}")
    return lines

# --- Streamlit UI ---
st.title("Game Build Optimizer")

character = st.selectbox("Choose your character", list(BASE_STATS.keys()))
money = st.number_input("How much money do you have?", min_value=0, value=20000, step=100)
optimization_target = st.selectbox("Select optimization target", list(target_relevant_stats.keys()))

base_stats = BASE_STATS[character]
available_items = [item for item in ITEM_POOL if item.character is None or item.character == character]
filtered_items = filter_items_for_target(available_items, optimization_target)

st.write(f"Items relevant to target: {len(filtered_items)}")

best_value = None
best_build = None

for r in range(1, 7):
    for combo in combinations(filtered_items, r):
        total_cost = sum(item.cost for item in combo)
        if total_cost > money:
            continue
        build_stats = calculate_build_stats(combo, base_stats)
        value = evaluate_build(build_stats, optimization_target, combo)
        if best_value is None or value > best_value:
            best_value = value
            best_build = combo

if best_build:
    st.subheader("Best Build Found:")
    st.write(f"Total Cost: {sum(item.cost for item in best_build)}")
    for item in best_build:
        st.write(f"- {item.name} ({item.cost})")
    st.subheader("Relevant Stats:")
    final_stats = calculate_build_stats(best_build, base_stats)
    for line in display_relevant_stats(final_stats, optimization_target):
        st.write(line)
    st.write(f"Optimization Value ({optimization_target}): {best_value:.3f}")
else:
    st.write("No valid build found within your budget.")
