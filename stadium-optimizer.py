import streamlit as st
from itertools import combinations
from typing import List, Dict

STAT_KEYS = [
    "HP", "Shields", "Armor", "Damage Reduction", "Total HP",
    "Weapon Power", "Ability Power", "Attack Speed", "Cooldown Reduction",
    "Max Ammo", "Weapon Lifesteal", "Ability Lifesteal", "Move Speed",
    "Reload Speed", "Melee Damage", "Critical Hit Damage"
]

OPTIMIZATION_TARGETS = STAT_KEYS + ["Effective HP", "Weapon DPS", "Ability DPS"]

class Item:
    def __init__(self, name: str, stats: Dict[str, float], cost: float):
        self.name = name
        self.stats = stats
        self.cost = cost

def combine_stats(items: List[Item]) -> Dict[str, float]:
    combined = {
        "HP": 0, "Shields": 0, "Armor": 0,
        "Damage Reduction": 0,
        "Weapon Power": 0,
        "Ability Power": 0,
        "Attack Speed": 0,
        "Cooldown Reduction": 1,
        "Max Ammo": 0,
        "Weapon Lifesteal": 0,
        "Ability Lifesteal": 0,
        "Move Speed": 0,
        "Reload Speed": 0,
        "Melee Damage": 0,
        "Critical Hit Damage": 0,
    }

    for item in items:
        for stat, value in item.stats.items():
            if stat == "Cooldown Reduction":
                combined[stat] *= (1 - value)
            elif stat in combined:
                combined[stat] += value
            else:
                combined[stat] = value

    combined["Damage Reduction"] = min(combined["Damage Reduction"], 1.0)
    combined["Total HP"] = combined["HP"] + combined["Shields"] + combined["Armor"]
    combined["Cooldown Reduction"] = 1 - combined["Cooldown Reduction"]

    return combined

def calculate_derived_stats(stats: Dict[str, float]) -> Dict[str, float]:
    effective_hp = (
        stats["Total HP"] / (1 - stats["Damage Reduction"])
        if (1 - stats["Damage Reduction"]) > 0 else float('inf')
    )
    base_weapon_damage = 100
    base_ability_damage = 100
    base_attack_speed = 1

    weapon_dps = base_weapon_damage * (1 + stats["Weapon Power"]) * (1 + stats["Attack Speed"]) * base_attack_speed
    ability_dps = base_ability_damage * (1 + stats["Ability Power"]) / (1 - stats["Cooldown Reduction"])

    return {
        "Effective HP": effective_hp,
        "Weapon DPS": weapon_dps,
        "Ability DPS": ability_dps,
    }

def evaluate_build(items: List[Item]) -> Dict[str, float]:
    combined_stats = combine_stats(items)
    derived_stats = calculate_derived_stats(combined_stats)
    combined_stats.update(derived_stats)
    return combined_stats

ITEM_POOL = [
    Item("Item A", {"HP": 50, "Weapon Power": 0.1, "Cooldown Reduction": 0.1}, cost=150),
    Item("Item B", {"Armor": 30, "Damage Reduction": 0.05, "Attack Speed": 0.05}, cost=120),
    Item("Item C", {"Shields": 40, "Ability Power": 0.15}, cost=180),
    Item("Item D", {"Max Ammo": 20, "Reload Speed": 0.1}, cost=90),
    Item("Item E", {"Melee Damage": 0.2, "Critical Hit Damage": 0.25}, cost=200),
    Item("Item F", {"Move Speed": 0.1, "Weapon Lifesteal": 0.05}, cost=110),
    Item("Item G", {"Ability Lifesteal": 0.07, "Cooldown Reduction": 0.15}, cost=170),
]

def format_stat(name, value):
    percent_stats = {
        "Weapon Power", "Ability Power", "Attack Speed",
        "Cooldown Reduction", "Damage Reduction",
        "Weapon Lifesteal", "Ability Lifesteal",
        "Move Speed", "Reload Speed",
        "Melee Damage", "Critical Hit Damage"
    }
    if name in percent_stats:
        return f"{value * 100:.2f}%"
    else:
        if abs(value - round(value)) < 1e-6:
            return str(int(round(value)))
        else:
            return f"{value:.2f}"

def display_stats(title: str, stats: Dict[str, float]):
    st.markdown(f"**{title}:**")
    for name, val in stats.items():
        st.markdown(f"- **{name}:** {format_stat(name, val)}")

def main():
    st.title("Game Build Optimizer")

    optimization_target = st.selectbox("Select Optimization Target:", OPTIMIZATION_TARGETS)
    budget = st.number_input("Enter your current budget (money):", min_value=0, value=500, step=10)

    max_build_size = min(6, len(ITEM_POOL))

    best_build = None
    best_score = float('-inf')
    best_stats = None
    best_cost = 0

    for r in range(1, max_build_size + 1):
        for combo in combinations(ITEM_POOL, r):
            total_cost = sum(item.cost for item in combo)
            if total_cost <= budget:
                stats = evaluate_build(combo)
                score = stats.get(optimization_target, 0)
                if score > best_score:
                    best_score = score
                    best_build = combo
                    best_stats = stats
                    best_cost = total_cost

    if best_build is None:
        st.warning("No builds found within your budget!")
    else:
        st.subheader(f"Best Build optimizing {optimization_target} within budget {budget}")
        st.markdown(f"**Total Cost:** {best_cost}")
        st.markdown("**Items:** " + ", ".join(item.name for item in best_build))
        st.markdown("---")

        derived_keys = {"Effective HP", "Weapon DPS", "Ability DPS"}

        normal_stats = {k: v for k, v in best_stats.items() if k not in derived_keys}
        derived_stats = {k: best_stats[k] for k in derived_keys if k in best_stats}

        display_stats("Stats", normal_stats)
        display_stats("Derived Stats", derived_stats)

if __name__ == "__main__":
    main()
