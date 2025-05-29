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

CHARACTERS = ["Juno", "Kiriko", "Mercy", "Mei"]

# Base stats per character
CHARACTER_BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0, "Damage Reduction": 0,
             "Weapon Power": 0, "Ability Power": 0, "Attack Speed": 0,
             "Cooldown Reduction": 0, "Max Ammo": 0, "Weapon Lifesteal": 0,
             "Ability Lifesteal": 0, "Move Speed": 0, "Reload Speed": 0,
             "Melee Damage": 0, "Critical Hit Damage": 0},

    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0, "Damage Reduction": 0,
               "Weapon Power": 0, "Ability Power": 0, "Attack Speed": 0,
               "Cooldown Reduction": 0, "Max Ammo": 0, "Weapon Lifesteal": 0,
               "Ability Lifesteal": 0, "Move Speed": 0, "Reload Speed": 0,
               "Melee Damage": 0, "Critical Hit Damage": 0},

    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0, "Damage Reduction": 0,
              "Weapon Power": 0, "Ability Power": 0, "Attack Speed": 0,
              "Cooldown Reduction": 0, "Max Ammo": 0, "Weapon Lifesteal": 0,
              "Ability Lifesteal": 0, "Move Speed": 0, "Reload Speed": 0,
              "Melee Damage": 0, "Critical Hit Damage": 0},

    "Mei": {"HP": 300, "Shields": 0, "Armor": 0, "Damage Reduction": 0,
            "Weapon Power": 0, "Ability Power": 0, "Attack Speed": 0,
            "Cooldown Reduction": 0, "Max Ammo": 0, "Weapon Lifesteal": 0,
            "Ability Lifesteal": 0, "Move Speed": 0, "Reload Speed": 0,
            "Melee Damage": 0, "Critical Hit Damage": 0},
}

class Item:
    def __init__(self, name: str, stats: Dict[str, float], cost: float, character: str = None):
        self.name = name
        self.stats = stats
        self.cost = cost
        self.character = character  # None means usable by all characters

def combine_stats(base_stats: Dict[str, float], items: List[Item]) -> Dict[str, float]:
    combined = base_stats.copy()

    # Initialize cooldown reduction as 1 (no reduction)
    cooldown_mult = 1.0

    for item in items:
        for stat, value in item.stats.items():
            if stat == "Cooldown Reduction":
                cooldown_mult *= (1 - value)
            elif stat in combined:
                combined[stat] += value
            else:
                combined[stat] = value

    combined["Cooldown Reduction"] = 1 - cooldown_mult
    combined["Damage Reduction"] = min(combined.get("Damage Reduction", 0), 1.0)
    combined["Total HP"] = combined.get("HP", 0) + combined.get("Shields", 0) + combined.get("Armor", 0)

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
    # Cooldown reduction applies only to Ability DPS
    ability_dps = base_ability_damage * (1 + stats["Ability Power"]) / (1 - stats["Cooldown Reduction"])

    return {
        "Effective HP": effective_hp,
        "Weapon DPS": weapon_dps,
        "Ability DPS": ability_dps,
    }

# Example items (add your own as needed)
ITEM_POOL = [
    Item("Item A", {"HP": 50, "Weapon Power": 0.1, "Cooldown Reduction": 0.1}, cost=150),
    Item("Item B", {"Armor": 30, "Damage Reduction": 0.05, "Attack Speed": 0.05}, cost=120),
    Item("Item C", {"Shields": 40, "Ability Power": 0.15}, cost=180),
    Item("Item D", {"Max Ammo": 20, "Reload Speed": 0.1}, cost=90),
    Item("Item E", {"Melee Damage": 0.2, "Critical Hit Damage": 0.25}, cost=200, character="Juno"),
    Item("Item F", {"Move Speed": 0.1, "Weapon Lifesteal": 0.05}, cost=110, character="Kiriko"),
    Item("Item G", {"Ability Lifesteal": 0.07, "Cooldown Reduction": 0.15}, cost=170, character="Mercy"),
    Item("Item H", {"HP": 70, "Armor": 20}, cost=130, character="Mei"),
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

def get_relevant_stats(target: str, all_stats: Dict[str, float]) -> Dict[str, float]:
    relevant_stats_map = {
        "HP": ["HP", "Shields", "Armor", "Total HP", "Damage Reduction", "Effective HP"],
        "Shields": ["Shields", "HP", "Armor", "Total HP"],
        "Armor": ["Armor", "HP", "Shields", "Total HP", "Damage Reduction", "Effective HP"],
        "Damage Reduction": ["Damage Reduction", "HP", "Shields", "Armor", "Effective HP"],
        "Total HP": ["Total HP", "HP", "Shields", "Armor", "Damage Reduction", "Effective HP"],

        "Weapon Power": ["Weapon Power", "Attack Speed", "Weapon DPS", "Cooldown Reduction"],
        "Ability Power": ["Ability Power", "Cooldown Reduction", "Ability DPS"],
        "Attack Speed": ["Attack Speed", "Weapon Power", "Weapon DPS"],
        "Cooldown Reduction": ["Cooldown Reduction", "Ability Power", "Ability DPS"],

        "Max Ammo": ["Max Ammo"],
        "Weapon Lifesteal": ["Weapon Lifesteal"],
        "Ability Lifesteal": ["Ability Lifesteal"],
        "Move Speed": ["Move Speed"],
        "Reload Speed": ["Reload Speed"],
        "Melee Damage": ["Melee Damage", "Critical Hit Damage"],
        "Critical Hit Damage": ["Critical Hit Damage", "Melee Damage"],

        "Effective HP": ["Effective HP", "Total HP", "Damage Reduction"],
        "Weapon DPS": ["Weapon DPS", "Weapon Power", "Attack Speed"],
        "Ability DPS": ["Ability DPS", "Ability Power", "Cooldown Reduction"],
    }
    keys_to_show = relevant_stats_map.get(target, [target])
    return {k: all_stats[k] for k in keys_to_show if k in all_stats}

def evaluate_build(base_stats: Dict[str, float], items: List[Item]) -> Dict[str, float]:
    combined_stats = combine_stats(base_stats, items)
    derived_stats = calculate_derived_stats(combined_stats)
    combined_stats.update(derived_stats)
    return combined_stats

def main():
    st.title("Game Build Optimizer")

    selected_character = st.selectbox("Select Character:", CHARACTERS)
    optimization_target = st.selectbox("Select Optimization Target:", OPTIMIZATION_TARGETS)
    budget = st.number_input("Enter your current budget (money):", min_value=0, value=500, step=10)

    base_stats = CHARACTER_BASE_STATS[selected_character]

    # Filter items for selected character
    available_items = [item for item in ITEM_POOL if (item.character is None or item.character == selected_character)]

    max_build_size = min(6, len(available_items))

    best_build = None
    best_score = float('-inf')
    best_stats = None
    best_cost = 0

    for r in range(1, max_build_size + 1):
        for combo in combinations(available_items, r):
            total_cost = sum(item.cost for item in combo)
            if total_cost <= budget:
                stats = evaluate_build(base_stats, combo)
                score = stats.get(optimization_target, 0)
                if score > best_score:
                    best_score = score
                    best_build = combo
                    best_stats = stats
                    best_cost = total_cost

    if best_build is None:
        st.warning("No builds found within your budget for the selected character!")
    else:
        st.subheader(f"Best Build for {selected_character} optimizing {optimization_target} within budget {budget}")
        st.markdown(f"**Total Cost:** {best_cost}")
        st.markdown("**Items:**")
        for item in best_build:
            st.markdown(f"- {item.name}")
        st.markdown("---")

        filtered_stats = get_relevant_stats(optimization_target, best_stats)
        display_stats("Relevant Stats", filtered_stats)

if __name__ == "__main__":
    main()
