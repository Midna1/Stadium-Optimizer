import streamlit as st
from itertools import combinations
from typing import List, Dict

# Define the stats keys we support
STAT_KEYS = [
    "HP", "Shields", "Armor", "Damage Reduction", "Total HP",
    "Weapon Power", "Ability Power", "Attack Speed", "Cooldown Reduction",
    "Max Ammo", "Weapon Lifesteal", "Ability Lifesteal", "Move Speed",
    "Reload Speed", "Melee Damage", "Critical Hit Damage"
]

# Optimization targets include all stats plus derived stats
OPTIMIZATION_TARGETS = STAT_KEYS + ["Effective HP", "Weapon DPS", "Ability DPS"]

class Item:
    def __init__(self, name: str, stats: Dict[str, float]):
        self.name = name
        self.stats = stats  # dictionary of stat name to value

def combine_stats(items: List[Item]) -> Dict[str, float]:
    """Combine stats from multiple items according to stacking rules."""
    combined = {
        "HP": 0, "Shields": 0, "Armor": 0,
        "Damage Reduction": 0,
        "Weapon Power": 0,
        "Ability Power": 0,
        "Attack Speed": 0,
        "Cooldown Reduction": 1,  # multiplicative
        "Max Ammo": 0,
        "Weapon Lifesteal": 0,
        "Ability Lifesteal": 0,
        "Move Speed": 0,
        "Reload Speed": 0,
        "Melee Damage": 0,
        "Critical Hit Damage": 0,
    }

    # Add stats
    for item in items:
        for stat, value in item.stats.items():
            if stat == "Cooldown Reduction":
                combined[stat] *= (1 - value)  # Multiplicative: cooldown reduction stacks multiplicatively, so multiply by (1 - each reduction)
            elif stat in combined:
                combined[stat] += value
            else:
                combined[stat] = value

    # Damage Reduction is additive but capped at 1.0 (100%)
    combined["Damage Reduction"] = min(combined["Damage Reduction"], 1.0)

    # Total HP is sum of HP, Shields, Armor
    combined["Total HP"] = combined["HP"] + combined["Shields"] + combined["Armor"]

    # Final cooldown reduction = 1 - product of (1 - individual cooldown reduction)
    combined["Cooldown Reduction"] = 1 - combined["Cooldown Reduction"]

    return combined

def calculate_derived_stats(stats: Dict[str, float]) -> Dict[str, float]:
    """Calculate derived stats like Effective HP, Weapon DPS, Ability DPS."""
    effective_hp = stats["Total HP"] / (1 - stats["Damage Reduction"]) if (1 - stats["Damage Reduction"]) > 0 else float('inf')
    # Assume base weapon damage and base ability damage = 100 for example
    base_weapon_damage = 100
    base_ability_damage = 100
    base_attack_speed = 1  # attacks per second
    weapon_dps = base_weapon_damage * (1 + stats["Weapon Power"]) * (1 + stats["Attack Speed"]) * base_attack_speed
    ability_dps = base_ability_damage * (1 + stats["Ability Power"]) / (1 - stats["Cooldown Reduction"])

    derived = {
        "Effective HP": effective_hp,
        "Weapon DPS": weapon_dps,
        "Ability DPS": ability_dps,
    }
    return derived

def evaluate_build(items: List[Item]) -> Dict[str, float]:
    combined_stats = combine_stats(items)
    derived_stats = calculate_derived_stats(combined_stats)
    combined_stats.update(derived_stats)
    return combined_stats

# Example pool of items with random/fake stats for demo
ITEM_POOL = [
    Item("Item A", {"HP": 50, "Weapon Power": 0.1, "Cooldown Reduction": 0.1}),
    Item("Item B", {"Armor": 30, "Damage Reduction": 0.05, "Attack Speed": 0.05}),
    Item("Item C", {"Shields": 40, "Ability Power": 0.15}),
    Item("Item D", {"Max Ammo": 20, "Reload Speed": 0.1}),
    Item("Item E", {"Melee Damage": 0.2, "Critical Hit Damage": 0.25}),
    Item("Item F", {"Move Speed": 0.1, "Weapon Lifesteal": 0.05}),
    Item("Item G", {"Ability Lifesteal": 0.07, "Cooldown Reduction": 0.15}),
]

def main():
    st.title("Game Build Optimizer")

    # User selects optimization target
    optimization_target = st.selectbox("Select Optimization Target:", OPTIMIZATION_TARGETS)

    # User selects items from pool, up to 6
    selected_names = st.multiselect(
        "Select up to 6 items to include in builds:",
        options=[item.name for item in ITEM_POOL],
        default=[],
        max_selections=6
    )

    if len(selected_names) == 0:
        st.info("Select at least one item to optimize builds.")
        return

    selected_items = [item for item in ITEM_POOL if item.name in selected_names]

    # Generate all combinations from length 1 to min(6, len(selected_items))
    max_build_size = min(6, len(selected_items))

    all_builds = []
    for r in range(1, max_build_size + 1):
        for combo in combinations(selected_items, r):
            stats = evaluate_build(combo)
            score = stats.get(optimization_target, 0)
            all_builds.append((combo, score, stats))

    # Sort builds by score descending
    all_builds.sort(key=lambda x: x[1], reverse=True)

    # Display top results
    st.subheader(f"Top Builds for optimizing {optimization_target}")
    max_results = st.slider("Number of top builds to display", 1, 20, 5)

    for idx, (combo, score, stats) in enumerate(all_builds[:max_results], start=1):
        st.markdown(f"### Build #{idx} (Score: {score:.3f})")
        st.markdown("**Items:** " + ", ".join(item.name for item in combo))
        st.markdown("**Stats:**")
        stats_display = {k: round(v, 4) for k, v in stats.items()}
        st.json(stats_display)

if __name__ == "__main__":
    main()
