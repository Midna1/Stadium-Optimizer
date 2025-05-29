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
    Item("Power Playbook", {"Ability Power": 0.10}, cost=1000, category="Ability", character=None),
    Item("Charged Plating", {"Armor": 25, "Ability Power": 0.10}, cost=1000, category="Ability", character=None),
    Item("Shady Spectacles", {"Ability Lifesteal": 0.10}, cost=1000, category="Ability", character=None),
    Item("Winning Attitude", {"HP": 25}, cost=1500, category="Ability", character=None),
    Item("Custom Stock", {"Weapon Power": 0.05, "Ability Power": 0.10}, cost=3750, category="Ability", character=None),
    Item("Biolight Overflow", {"HP": 25, "Ability Power": 0.05}, cost=4000, category="Ability", character=None),
    Item("Energized Bracers", {"Ability Power": 0.10, "Ability Lifesteal": 0.10}, cost=4000, category="Ability", character=None),
    Item("Junker Whatchamajig", {}, cost=4000, category="Ability", character=None),
    Item("Wrist Wraps", {"Ability Power": 0.05, "Attack Speed": 0.10}, cost=4000, category="Ability", character=None),
    Item("Multi-Tool", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, cost=4500, category="Ability", character=None),
    Item("Nano-Cola", {"Ability Power": 0.20}, cost=6000, category="Ability", character=None),
    Item("Three-Tap Tommygun", {"Ability Power": 0.10, "Attack Speed": 0.10}, cost=9500, category="Ability", character=None),
    Item("Biotech Maximizer", {"HP": 25, "Ability Power": 0.10}, cost=10000, category="Ability", character=None),
    Item("Catalytic Crystal", {"Ability Power": 0.15}, cost=10000, category="Ability", character=None),
    Item("Lumerico Fusion Drive", {"Armor": 50, "Ability Power": 0.15}, cost=10000, category="Ability", character=None),
    Item("Superflexor", {"HP": 25, "Weapon Power": 0.10, "Ability Power": 0.25}, cost=10000, category="Ability", character=None),
    Item("Cybervenom", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, cost=10500, category="Ability", character=None),
    Item("Iridescent Iris", {"Ability Power": 0.20, "Cooldown Reduction": 0.10}, cost=11000, category="Ability", character=None),
    Item("Liquid Nitrogen", {"HP": 25, "Ability Power": 0.10}, cost=11000, category="Ability", character=None),
    Item("Mark of the Kitsune", {"Ability Power": 0.10}, cost=11000, category="Ability", character=None),
    Item("Champion's Kit", {"Ability Power": 0.40}, cost=13500, category="Ability", character=None),


    

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
    # Start with a full copy of base stats
    stats = {
        "HP": base_stats.get("HP", 0),
        "Shields": base_stats.get("Shields", 0),
        "Armor": base_stats.get("Armor", 0),
        "Max Ammo": 0,
        "Weapon Power": 0.0,
        "Ability Power": 0.0,
        "Attack Speed": 0.0,
        "Reload Speed": 0.0,
        "Cooldown Reduction": 1.0,  # multiplicative, so we multiply (1 - x)
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
                stats[stat] = val  # fallback just in case

    # Ensure cooldown doesn't go below a hard floor (e.g. 90% reduction is minimum)
    if stats["Cooldown Reduction"] < 0.1:
        stats["Cooldown Reduction"] = 0.1

    # Finalize Ability Power with cooldown applied
    stats["Ability Power"] *= stats["Cooldown Reduction"]

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
