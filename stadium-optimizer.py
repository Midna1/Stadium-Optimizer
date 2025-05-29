import streamlit as st
from itertools import combinations

# --- Your Item class ---
class Item:
    def __init__(self, name, stats, cost, category, character=None):
        self.name = name
        self.stats = stats  # dict of stat_name: value
        self.cost = cost
        self.category = category  # "Weapon", "Ability", "Survival"
        self.character = character  # None or character string

# --- Your item pool here (just a few example items for demo) ---
ITEM_POOL = [
    Item("Shield Booster", {"Shields": 100}, 150, "Survival"),
    Item("Power Amp", {"Weapon Power": 0.15}, 200, "Weapon"),
    Item("Quick Reload", {"Reload Speed": 0.2}, 180, "Weapon"),
    Item("Ability Surge", {"Ability Power": 0.25, "Cooldown Reduction": 0.1}, 220, "Ability"),
    Item("Speed Boots", {"Move Speed": 0.15}, 120, "Survival"),
    Item("Juno's Blessing", {"HP": 75}, 100, "Survival", character="Juno"),
    Item("Kiriko's Charm", {"Ability Power": 0.3}, 250, "Ability", character="Kiriko"),
    # ... add your full 50 items here ...
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
    "Ability DPS": {"Ability Power", "Cooldown Reduction", "Ability Lifesteal"},
}

def filter_items_for_target(items, target):
    relevant_stats = target_relevant_stats.get(target, set())
    return [
        item for item in items
        if any(stat in relevant_stats for stat in item.stats.keys())
    ]

def calculate_build_stats(items, base_stats):
    stats = base_stats.copy()
    additive_stats = {
        "Weapon Power": 0.0,
        "Ability Power": 0.0,
        "Attack Speed": 0.0,
        "Cooldown Reduction": 1.0,  # multiplicative
        "Reload Speed": 0.0,
        "Damage Reduction": 0.0,
        "Weapon Lifesteal": 0.0,
        "Ability Lifesteal": 0.0,
        "Move Speed": 0.0,
        "Critical Hit Damage": 0.0,
        "Melee Damage": 0.0,
        "Max Ammo": 0,
    }
    for key in ["HP", "Shields", "Armor"]:
        if key not in stats:
            stats[key] = 0

    for item in items:
        for stat, val in item.stats.items():
            if stat in {"HP", "Shields", "Armor", "Max Ammo"}:
                stats[stat] += val
            elif stat == "Cooldown Reduction":
                additive_stats["Cooldown Reduction"] *= (1 - val)
            else:
                additive_stats[stat] = additive_stats.get(stat, 0) + val

    if additive_stats["Cooldown Reduction"] < 0.1:
        additive_stats["Cooldown Reduction"] = 0.1

    stats["Weapon Power"] = additive_stats["Weapon Power"]
    stats["Ability Power"] = additive_stats["Ability Power"] * additive_stats["Cooldown Reduction"]
    stats["Attack Speed"] = additive_stats["Attack Speed"]
    stats["Reload Speed"] = additive_stats["Reload Speed"]
    stats["Damage Reduction"] = additive_stats["Damage Reduction"]
    stats["Weapon Lifesteal"] = additive_stats["Weapon Lifesteal"]
    stats["Ability Lifesteal"] = additive_stats["Ability Lifesteal"]
    stats["Move Speed"] = additive_stats["Move Speed"]
    stats["Critical Hit Damage"] = additive_stats["Critical Hit Damage"]
    stats["Melee Damage"] = additive_stats["Melee Damage"]
    stats["Max Ammo"] = stats.get("Max Ammo", 0) + additive_stats.get("Max Ammo", 0)

    return stats

def evaluate_build(stats, target):
    if target == "HP":
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
    elif target == "Ability DPS":
        base_ability_dps = 80
        ability_power = 1 + stats.get("Ability Power", 0)
        cooldown_mult = stats.get("Cooldown Reduction", 1.0)
        ability_lifesteal = 1 + stats.get("Ability Lifesteal", 0)
        return base_ability_dps * ability_power * (1 / cooldown_mult) * ability_lifesteal
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
        value = evaluate_build(build_stats, optimization_target)
        if best_value is None or value > best_value:
            best_value = value
            best_build = combo

if best_build:
    st.subheader("Best Build Found:")
    st.write(f"Total Cost: {sum(item.cost for item in best_build)}")
    for item in best_build:
        st.markdown(f"**{item.name}** (Cost: {item.cost}, Category: {item.category})")
        # Display item stats vertically
        for stat, val in item.stats.items():
            if isinstance(val, float) and abs(val) < 10:
                st.write(f"- {stat}: {val*100:.1f}%")
            else:
                st.write(f"- {stat}: {val}")

    # Show final build stats relevant to target
    st.subheader(f"Build Stats Relevant to '{optimization_target}':")
    final_stats = calculate_build_stats(best_build, base_stats)
    for line in display_relevant_stats(final_stats, optimization_target):
        st.write(line)
    st.write(f"Optimization Value ({optimization_target}): {best_value:.3f}")
else:
    st.write("No valid build found within your budget.")
