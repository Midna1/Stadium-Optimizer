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
    Item("Item_1", {"Shields": 71, "Reload Speed": 0.288}, cost=194, category="Survival", character=None),
    Item("Item_2", {"Weapon Power": 0.109, "Cooldown Reduction": 0.159}, cost=263, category="Ability", character=None),
    Item("Item_3", {"Move Speed": 0.112}, cost=187, category="Ability", character="Juno"),
    Item("Item_4", {"Critical Hit Damage": 0.159, "Armor": 101}, cost=154, category="Weapon", character=None),
    Item("Item_5", {"Shields": 63, "Ability Power": 0.06, "Weapon Lifesteal": 0.192}, cost=121, category="Weapon", character=None),
    Item("Item_6", {"Cooldown Reduction": 0.143, "HP": 118}, cost=196, category="Ability", character=None),
    Item("Item_7", {"Melee Damage": 0.177, "Damage Reduction": 0.069}, cost=167, category="Weapon", character=None),
    Item("Item_8", {"Ability Power": 0.276}, cost=179, category="Ability", character=None),
    Item("Item_9", {"HP": 63, "Ability Lifesteal": 0.152}, cost=286, category="Survival", character=None),
    Item("Item_10", {"Move Speed": 0.102, "Weapon Power": 0.171}, cost=90, category="Weapon", character=None),
    Item("Item_11", {"Shields": 44, "Reload Speed": 0.167}, cost=259, category="Survival", character="Kiriko"),
    Item("Item_12", {"Max Ammo": 129, "Critical Hit Damage": 0.13}, cost=184, category="Weapon", character=None),
    Item("Item_13", {"Cooldown Reduction": 0.099, "Ability Lifesteal": 0.096}, cost=203, category="Ability", character=None),
    Item("Item_14", {"Attack Speed": 0.117}, cost=84, category="Weapon", character=None),
    Item("Item_15", {"Armor": 105, "HP": 102}, cost=95, category="Survival", character=None),
    Item("Item_16", {"Ability Power": 0.267, "Weapon Lifesteal": 0.071}, cost=150, category="Ability", character=None),
    Item("Item_17", {"Reload Speed": 0.268}, cost=217, category="Survival", character="Mercy"),
    Item("Item_18", {"Damage Reduction": 0.111, "Melee Damage": 0.181}, cost=270, category="Weapon", character=None),
    Item("Item_19", {"HP": 39, "Move Speed": 0.184}, cost=83, category="Survival", character=None),
    Item("Item_20", {"Shields": 70, "Weapon Power": 0.064}, cost=114, category="Weapon", character=None),
    Item("Item_21", {"Ability Power": 0.077, "Attack Speed": 0.107}, cost=181, category="Ability", character=None),
    Item("Item_22", {"Cooldown Reduction": 0.287}, cost=294, category="Ability", character=None),
    Item("Item_23", {"Critical Hit Damage": 0.2, "Armor": 51}, cost=147, category="Weapon", character=None),
    Item("Item_24", {"Max Ammo": 55}, cost=274, category="Survival", character=None),
    Item("Item_25", {"Weapon Lifesteal": 0.059, "Move Speed": 0.276}, cost=166, category="Survival", character=None),
    Item("Item_26", {"Ability Lifesteal": 0.052, "Cooldown Reduction": 0.051}, cost=171, category="Ability", character=None),
    Item("Item_27", {"HP": 44}, cost=54, category="Survival", character=None),
    Item("Item_28", {"Melee Damage": 0.261, "Critical Hit Damage": 0.119}, cost=260, category="Weapon", character=None),
    Item("Item_29", {"Armor": 146}, cost=143, category="Survival", character=None),
    Item("Item_30", {"Reload Speed": 0.095, "Ability Power": 0.09}, cost=93, category="Ability", character="Mei"),
    Item("Item_31", {"Weapon Power": 0.115, "Attack Speed": 0.263}, cost=104, category="Weapon", character=None),
    Item("Item_32", {"HP": 54, "Shields": 70}, cost=284, category="Survival", character=None),
    Item("Item_33", {"Move Speed": 0.102, "Weapon Lifesteal": 0.131}, cost=236, category="Survival", character=None),
    Item("Item_34", {"Cooldown Reduction": 0.138, "Ability Power": 0.218}, cost=289, category="Ability", character=None),
    Item("Item_35", {"Attack Speed": 0.165, "Reload Speed": 0.184}, cost=59, category="Weapon", character=None),
    Item("Item_36", {"Damage Reduction": 0.05, "Armor": 135}, cost=289, category="Survival", character=None),
    Item("Item_37", {"Weapon Power": 0.109}, cost=107, category="Weapon", character="Kiriko"),
    Item("Item_38", {"HP": 75, "Cooldown Reduction": 0.17}, cost=124, category="Ability", character=None),
    Item("Item_39", {"Max Ammo": 112, "Reload Speed": 0.079}, cost=166, category="Survival", character=None),
    Item("Item_40", {"Shields": 89, "Ability Lifesteal": 0.131}, cost=174, category="Ability", character=None),
    Item("Item_41", {"Melee Damage": 0.199}, cost=199, category="Weapon", character=None),
    Item("Item_42", {"Critical Hit Damage": 0.092}, cost=79, category="Weapon", character=None),
    Item("Item_43", {"Armor": 69, "Damage Reduction": 0.112}, cost=212, category="Survival", character="Mercy"),
    Item("Item_44", {"Weapon Lifesteal": 0.084}, cost=256, category="Survival", character=None),
    Item("Item_45", {"Ability Power": 0.111}, cost=89, category="Ability", character=None),
    Item("Item_46", {"HP": 101, "Move Speed": 0.212}, cost=298, category="Survival", character=None),
    Item("Item_47", {"Cooldown Reduction": 0.088, "Attack Speed": 0.18}, cost=114, category="Ability", character=None),
    Item("Item_48", {"Weapon Power": 0.164, "Melee Damage": 0.064}, cost=287, category="Weapon", character=None),
    Item("Item_49", {"Reload Speed": 0.13, "Ability Lifesteal": 0.087}, cost=294, category="Ability", character=None),
    Item("Item_50", {"Damage Reduction": 0.113, "Armor": 81}, cost=234, category="Survival", character=None),
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
