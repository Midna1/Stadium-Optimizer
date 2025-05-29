import streamlit as st
from itertools import combinations

# --- Item class ---
class Item:
    def __init__(self, name, stats, cost, category, character=None, extra_effect=None):
        self.name = name
        self.stats = stats  # dict of stat_name: value
        self.cost = cost
        self.category = category  # "Weapon", "Ability", "Survival"
        self.character = character  # None or character string
        self.extra_effect = extra_effect  # function(stats) -> dict or None

# --- Extra effects ---
def vishkar_condensor_effect(stats):
    hp = stats.get("HP", 0)
    if hp > 100:
        return {"HP": -100, "Shields": 100}
    else:
        return {"HP": -hp, "Shields": hp}

# --- Item pool ---
ITEM_POOL = [
    # Ability items (sample subset)
    Item("Power Playbook", {"Ability Power": 0.10}, 1000, "Ability"),
    Item("Charged Plating", {"Armor": 25, "Ability Power": 0.10}, 1000, "Ability"),
    Item("Shady Spectacles", {"Ability Lifesteal": 0.10}, 1000, "Ability"),
    Item("Winning Attitude", {"HP": 25}, 1500, "Ability"),
    # ... other Ability items omitted for brevity ...

    # Juno-specific items
    Item("Lock-On Shield", {"Ability Power": 0.1001}, 4000, "Survival", character="Juno"),
    Item("Lux Loop", {"Ability Power": 0.1001}, 4000, "Ability", character="Juno"),
    Item("Pulsar Torpedos", {"Ability Lifesteal": 0.10}, 10000, "Ability", character="Juno",
         extra_effect=lambda stats: {"Bonus Damage": 20 * (1 + stats.get("Ability Power", 0.0))}),
    Item("Solar Shielding", {"Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Red Promise Regulator", {"Shields": 50, "Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Boosted Rockets", {"Shields": 25}, 4000, "Survival", character="Juno"),
    Item("Forti-Glide", {"Shields": 75, "Damage Reduction": 0.10}, 10000, "Survival", character="Juno"),
    Item("Sunburst Serum", {"Shields": 75}, 10000, "Survival", character="Juno"),

    # New Survival items
    Item("Field Rations", {"HP": 10}, 1000, "Survival"),
    Item("Running Shoes", {"HP": 10}, 1000, "Survival"),
    Item("Adrenaline Shot", {"HP": 25}, 1500, "Survival"),
    Item("Armored Vest", {"Armor": 25}, 1500, "Survival"),
    Item("Electrolytes", {}, 1500, "Survival"),
    Item("First Aid Kit", {"Shields": 25}, 1500, "Survival"),
    Item("Heartbeat Sensor", {"Move Speed": 5}, 1500, "Survival"),
    Item("Siphon Gloves", {"HP": 25}, 1500, "Survival"),
    Item("Reinforced Titanium", {"Shields": 25}, 3750, "Survival"),
    Item("Cushioned Padding", {"Shields": 25}, 4000, "Survival"),
    Item("Ironclad Exhaust Ports", {"Cooldown Reduction": 0.05}, 4000, "Survival"),
    Item("Vishkar Condensor", {"Shields": 25}, 4000, "Survival", extra_effect=vishkar_condensor_effect),
]

# --- Base stats ---
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# --- Relevant stats by optimization target ---
target_relevant_stats = {
    "HP": {"HP"},
    "Shields": {"Shields"},
    "Armor": {"Armor"},
    "Damage Reduction": {"Damage Reduction"},
    "Total HP": {"HP", "Shields", "Armor"},
    "Weapon Power": {"Weapon Power"},
    "Ability Damage": {"Ability Power", "Cooldown Reduction"},
    "Ability DPS": {"Ability Power", "Cooldown Reduction"},
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
}

def filter_items_for_target(items, target):
    relevant_stats = target_relevant_stats.get(target, set())
    filtered = []
    for item in items:
        # Include if item provides relevant stats or is Lock-On Shield for HP/Shield targets
        if any(stat in relevant_stats for stat in item.stats.keys()):
            filtered.append(item)
        elif item.name == "Lock-On Shield" and target in {"HP", "Shields", "Effective HP", "Total HP"}:
            filtered.append(item)
    return filtered

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
        "Bonus Damage": 0.0,
    }

    # Add item stats
    for item in items:
        for stat, val in item.stats.items():
            if stat == "Cooldown Reduction":
                stats["Cooldown Reduction"] *= (1 - val)
            elif stat in stats:
                stats[stat] += val

    # Apply extra_effects that return dicts of stat modifications
    for item in items:
        if item.extra_effect:
            effect_result = item.extra_effect(stats)
            if isinstance(effect_result, dict):
                for stat, val in effect_result.items():
                    if stat == "Cooldown Reduction":
                        stats["Cooldown Reduction"] *= (1 - val)
                    elif stat in stats:
                        stats[stat] += val

    # Clamp cooldown reduction minimum
    stats["Cooldown Reduction"] = max(stats["Cooldown Reduction"], 0.1)

    # Apply cooldown reduction multiplier to Ability Power
    stats["Ability Power"] *= stats["Cooldown Reduction"]

    # Lock-On Shield extra: 50% of Shields added to HP
    if any(item.name == "Lock-On Shield" for item in items):
        stats["HP"] += 0.5 * stats["Shields"]

    return stats

def evaluate_build(stats, target, items):
    base_damage = 100
    ap = stats.get("Ability Power", 0.0)
    bonus = stats.get("Bonus Damage", 0.0)

    if target == "Ability Damage":
        return base_damage * (1 + ap) + bonus
    elif target == "Ability DPS":
        base_cooldown = 6
        effective_cd = base_cooldown * stats.get("Cooldown Reduction", 1.0)
        total_damage = base_damage * (1 + ap) + bonus
        return total_damage / effective_cd if effective_cd > 0 else 0
    elif target == "HP":
        return stats.get("HP", 0)
    elif target == "Shields":
        return stats.get("Shields", 0)
    elif target == "Armor":
        return stats.get("Armor", 0)
    elif target == "Total HP":
        return stats.get("HP", 0) + stats.get("Shields", 0) + stats.get("Armor", 0)
    elif target == "Weapon Power":
        return stats.get("Weapon Power", 0)
    elif target == "Cooldown Reduction":
        return 1 - stats.get("Cooldown Reduction", 1.0)
    elif target == "Weapon DPS":
        return 100 * (1 + stats["Weapon Power"]) * (1 + stats["Attack Speed"]) * (1 + stats["Reload Speed"]) * (1 + stats["Critical Hit Damage"])
    elif target == "Effective HP":
        total = stats["HP"] + stats["Shields"] + stats["Armor"]
        dr = min(stats["Damage Reduction"], 0.99)
        return total / (1 - dr)
    else:
        return stats.get(target, 0)

def display_relevant_stats(stats, target):
    relevant_stats = target_relevant_stats.get(target, set())
    lines = []
    for s in ["HP", "Shields", "Armor"]:
        if s in relevant_stats or target in ["Total HP", "Effective HP"]:
            lines.append(f"{s}: {stats.get(s, 0)}")
    for stat in relevant_stats:
        if stat in ["HP", "Shields", "Armor"]:
            continue
        val = stats.get(stat)
        if val is None:
            continue
        if isinstance(val, float) and abs(val) < 10:
            lines.append(f"{stat}: {val*100:.1f}%")
        else:
            lines.append(f"{stat}: {val}")
    return lines

# --- Streamlit UI ---
st.title("Game Build Optimizer")

character = st.selectbox("Choose your character", list(BASE_STATS.keys()))
money = st.number_input("Enter your money budget", min_value=0, max_value=100000, value=10000, step=500)

target = st.selectbox("Choose optimization target", list(target_relevant_stats.keys()))

# Filter items by character and target
filtered_items = [item for item in ITEM_POOL if (item.character is None or item.character == character)]
filtered_items = filter_items_for_target(filtered_items, target)

max_items = st.slider("Maximum number of items to buy", 1, 5, 3)

st.write(f"Filtering {len(filtered_items)} items for {target} optimization.")

best_score = -float('inf')
best_build = None

with st.spinner("Calculating best build... This may take a while."):
    # Generate combinations of filtered items
    for r in range(1, max_items + 1):
        for combo in combinations(filtered_items, r):
            total_cost = sum(item.cost for item in combo)
            if total_cost <= money:
                stats = calculate_build_stats(combo, BASE_STATS[character])
                score = evaluate_build(stats, target, combo)
                if score > best_score:
                    best_score = score
                    best_build = combo

if best_build:
    st.header("Best Build Found")
    for item in best_build:
        st.write(f"- {item.name} (Cost: {item.cost})")
    st.write(f"Total Cost: {sum(item.cost for item in best_build)}")
    stats = calculate_build_stats(best_build, BASE_STATS[character])
    st.write(f"**{target} score:** {best_score:.2f}")
    st.write("Stats breakdown:")
    for line in display_relevant_stats(stats, target):
        st.write(line)
else:
    st.write("No valid build found within budget.")

