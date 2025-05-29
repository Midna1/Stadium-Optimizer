import streamlit as st
from itertools import combinations

# --- Item class ---
class Item:
    def __init__(self, name, stats, cost, category, character=None, extra_effect=None):
        self.name = name
        self.stats = stats  # dict of stat_name: value
        self.cost = cost
        self.category = category
        self.character = character
        self.extra_effect = extra_effect  # Optional function for special effects

# --- Special effect function for Pulsar Torpedos ---
def pulsar_torpedos_effect(stats):
    # Adds 20 base damage + 50% of ability power (expressed as percentage, e.g. 0.10)
    ability_power = stats.get("Ability Power", 0)
    return 20 + 0.5 * ability_power * 100
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
    Item("Pulsar Torpedos", {"Ability Lifesteal": 0.10}, cost=10000, category="Ability", character="Juno"),
    Item("Solar Shielding", {"Ability Power": 0.15}, cost=10000, category="Ability", character="Juno"),
    Item("Red Promise Regulator", {"Shields": 50, "Ability Power": 0.15}, cost=10000, category="Ability", character="Juno"),

    
]

# --- Base stats per character ---
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# --- Optimization targets and relevant stats ---
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
    "Ability DPS": {"Ability Power", "Cooldown Reduction"},  # Ability Lifesteal excluded by your request
}

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
        "Cooldown Reduction": 1.0,  # multiplicative
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

        # Apply extra effects from items (e.g., Pulsar Torpedos)
        extra_damage = sum(item.extra_effect(stats) for item in items if item.extra_effect)

        return (base_ability_dps + extra_damage) * ability_power * (1 / cooldown_mult)
    elif target == "HP":
        return stats.get("HP", 0)
    elif target == "Shields":
        return stats.get("Shields", 0)
    elif target == "Armor":
        return stats.get("Armor", 0)
    elif target == "Damage Reduction":
        return stats.get("Damage Reduction", 0)
    elif target == "Total HP":
        return stats.get("HP", 0) + stats.get("Shields", 0) + stats.get("Armor", 0)
    elif target == "Weapon Power":
        return stats.get("Weapon Power", 0)
    elif target == "Ability Power":
        return stats.get("Ability Power", 0)
    elif target == "Attack Speed":
        return stats.get("Attack Speed", 0)
    elif target == "Cooldown Reduction":
        return 1 - stats.get("Ability Power", 1)
    elif target == "Max Ammo":
        return stats.get("Max Ammo", 0)
    elif target == "Weapon Lifesteal":
        return stats.get("Weapon Lifesteal", 0)
    elif target == "Ability Lifesteal":
        return stats.get("Ability Lifesteal", 0)
    elif target == "Move Speed":
        return stats.get("Move Speed", 0)
    elif target == "Reload Speed":
        return stats.get("Reload Speed", 0)
    elif target == "Melee Damage":
        return stats.get("Melee Damage", 0)
    elif target == "Critical Hit Damage":
        return stats.get("Critical Hit Damage", 0)
    elif target == "Effective HP":
        total_hp = stats.get("HP", 0) + stats.get("Shields", 0) + stats.get("Armor", 0)
        dmg_red = stats.get("Damage Reduction", 0)
        if dmg_red >= 1.0:
            dmg_red = 0.99
        return total_hp / (1 - dmg_red)
    elif target == "Weapon DPS":
        base_dps = 100
        weapon_power = 1 + stats.get("Weapon Power", 0)
        attack_speed = 1 + stats.get("Attack Speed", 0)
        reload_speed = 1 + stats.get("Reload Speed", 0)
        crit_damage = 1 + stats.get("Critical Hit Damage", 0)
        return base_dps * weapon_power * attack_speed * reload_speed * crit_damage
    else:
        return 0

def display_relevant_stats(stats, target):
    relevant_stats = target_relevant_stats.get(target, set())
    lines = []
    for base_stat in ["HP", "Shields", "Armor"]:
        if base_stat in relevant_stats or target in ["Total HP", "Effective HP"]:
            val = stats.get(base_stat, 0)
            lines.append(f"{base_stat}: {val}")

    for stat in relevant_stats:
        if stat in ["HP", "Shields", "Armor"]:
            continue
        val = stats.get(stat)
        if val is not None:
            if isinstance(val, float) and abs(val) < 10:
                lines.append(f"{stat}: {val*100:.1f}%")
            else:
                lines.append(f"{stat}: {val}")
    return lines

# --- Streamlit UI ---
st.title("Game Build Optimizer")

character = st.selectbox("Choose your character", list(BASE_STATS.keys()))
money = st.number_input("How much money do you have?", min_value=0, value=500, step=10)
optimization_target = st.selectbox("Select optimization target", list(target_relevant_stats.keys()))

available_items = [item for item in ITEM_POOL if item.character is None or item.character == character]
filtered_items = filter_items_for_target(available_items, optimization_target)

st.write(f"Items relevant to target: {len(filtered_items)}")

base_stats = BASE_STATS[character]

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
        st.markdown(f"**{item.name}**")

    st.subheader(f"Build Stats Relevant to '{optimization_target}':")
    final_stats = calculate_build_stats(best_build, base_stats)
    for line in display_relevant_stats(final_stats, optimization_target):
        st.write(line)
    st.write(f"Optimization Value ({optimization_target}): {best_value:.3f}")
else:
    st.write("No valid build found within your budget.")
