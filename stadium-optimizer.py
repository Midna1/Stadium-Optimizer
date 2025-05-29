import streamlit as st
from itertools import combinations

# --- Item class ---
class Item:
    def __init__(self, name, stats, cost, category, character=None):
        self.name = name
        self.stats = stats  # dict of stat_name: value
        self.cost = cost
        self.category = category  # "Weapon", "Ability", "Survival"
        self.character = character  # None or character string

# --- Your item pool ---
ITEM_POOL = [
    Item("Power Playbook", {"Ability Power": 0.10}, cost=1000, category="Ability"),
    Item("Charged Plating", {"Armor": 25, "Ability Power": 0.10}, cost=1000, category="Ability"),
    Item("Shady Spectacles", {"Ability Lifesteal": 0.10}, cost=1000, category="Ability"),
    Item("Winning Attitude", {"HP": 25}, cost=1500, category="Ability"),
    Item("Custom Stock", {"Weapon Power": 0.05, "Ability Power": 0.10}, cost=3750, category="Ability"),
    Item("Biolight Overflow", {"HP": 25, "Ability Power": 0.05}, cost=4000, category="Ability"),
    Item("Energized Bracers", {"Ability Power": 0.10, "Ability Lifesteal": 0.10}, cost=4000, category="Ability"),
    Item("Junker Whatchamajig", {}, cost=4000, category="Ability"),
    Item("Wrist Wraps", {"Ability Power": 0.05, "Attack Speed": 0.10}, cost=4000, category="Ability"),
    Item("Multi-Tool", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, cost=4500, category="Ability"),
    Item("Nano-Cola", {"Ability Power": 0.20}, cost=6000, category="Ability"),
    Item("Three-Tap Tommygun", {"Ability Power": 0.10, "Attack Speed": 0.10}, cost=9500, category="Ability"),
    Item("Biotech Maximizer", {"HP": 25, "Ability Power": 0.10}, cost=10000, category="Ability"),
    Item("Catalytic Crystal", {"Ability Power": 0.15}, cost=10000, category="Ability"),
    Item("Lumerico Fusion Drive", {"Armor": 50, "Ability Power": 0.15}, cost=10000, category="Ability"),
    Item("Superflexor", {"HP": 25, "Weapon Power": 0.10, "Ability Power": 0.25}, cost=10000, category="Ability"),
    Item("Cybervenom", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, cost=10500, category="Ability"),
    Item("Iridescent Iris", {"Ability Power": 0.20, "Cooldown Reduction": 0.10}, cost=11000, category="Ability"),
    Item("Liquid Nitrogen", {"HP": 25, "Ability Power": 0.10}, cost=11000, category="Ability"),
    Item("Mark of the Kitsune", {"Ability Power": 0.10}, cost=11000, category="Ability"),
    Item("Champion's Kit", {"Ability Power": 0.40}, cost=13500, category="Ability"),
]

# --- Base stats for each character ---
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# --- Relevant stats per optimization target ---
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
    " Ammo": {" Ammo"},
    "Weapon Lifesteal": {"Weapon Lifesteal"},
    "Ability Lifesteal": {"Ability Lifesteal"},
    "Move Speed": {"Move Speed"},
    "Reload Speed": {"Reload Speed"},
    "Melee Damage": {"Melee Damage"},
    "Critical Hit Damage": {"Critical Hit Damage"},
    "Effective HP": {"HP", "Shields", "Armor", "Damage Reduction"},
    "Weapon DPS": {"Weapon Power", "Attack Speed", "Reload Speed", "Critical Hit Damage"},
    # Ability DPS excludes Ability Lifesteal now
    "Ability DPS": {"Ability Power", "Cooldown Reduction"},
}

def filter_items_for_target(items, target):
    relevant_stats = target_relevant_stats.get(target, set())
    return [
        item for item in items
        if any(stat in relevant_stats for stat in item.stats.keys())
    ]

def calculate_build_stats(items, base_stats):
    # Start with a copy of base stats
    stats = {
        "HP": base_stats.get("HP", 0),
        "Shields": base_stats.get("Shields", 0),
        "Armor": base_stats.get("Armor", 0),
        " Ammo": 0,
        "Weapon Power": 0.0,
        "Ability Power": 0.0,
        "Attack Speed": 0.0,
        "Reload Speed": 0.0,
        "Cooldown Reduction": 1.0,  # multiplicative cooldown multiplier
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
                stats["Cooldown Reduction"] *= (1 - val)  # multiply cooldown reductions
            elif stat in stats:
                stats[stat] += val
            else:
                stats[stat] = val  # fallback for new stats

    # Minimum cooldown floor (e.g. 90% reduction )
    if stats["Cooldown Reduction"] < 0.1:
        stats["Cooldown Reduction"] = 0.1

    # Apply cooldown multiplier to Ability Power for effective ability DPS
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
        return 1 - stats.get("Cooldown Reduction", 1)
    elif target == " Ammo":
        return stats.get(" Ammo", 0)
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
        # Ability Lifesteal is excluded from Ability DPS calculation now
        ability_power = 1 + stats.get("Ability Power", 0)
        # cooldown reduction is already applied in ability_power in calculate_build_stats
        return base_ability_dps * ability_power
    else:
        return 0

# --- Streamlit UI and optimization ---
def main():
    st.title("Item Build Optimizer")

    character = st.selectbox("Select Character", list(BASE_STATS.keys()))
    target = st.selectbox("Optimize For", list(target_relevant_stats.keys()))
    _cost = st.number_input(" Total Cost", min_value=0, value=15000, step=500)

    filtered_items = filter_items_for_target(ITEM_POOL, target)

    st.write(f"Number of relevant items: {len(filtered_items)}")

    best_score = -float("inf")
    best_build = None

    # For demonstration: limit  combo size to 4 to keep computation reasonable
    max_items = 6

    for r in range(1, max_items + 1):
        for combo in combinations(filtered_items, r):
            total_cost = sum(item.cost for item in combo)
            if total_cost > max_cost:
                continue

            stats = calculate_build_stats(combo, BASE_STATS[character])
            score = evaluate_build(stats, target)

            if score > best_score:
                best_score = score
                best_build = combo

    if best_build:
        st.subheader("Best Build Found")
        for item in best_build:
            st.write(f"{item.name} - Cost: {item.cost}, Stats: {item.stats}")
        st.write(f"Total Cost: {sum(item.cost for item in best_build)}")
        st.write(f"Score for {target}: {best_score:.4f}")
    else:
        st.write("No valid build found with current constraints.")

if __name__ == "__main__":
    main()
