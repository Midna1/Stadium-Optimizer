# streamlit_build_optimizer_v2.py
import streamlit as st
from functools import lru_cache
from itertools import combinations
from typing import List, Dict, Tuple, Optional
import math
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# Item class
# -------------------------
class Item:
    def __init__(self, name: str, stats: Dict[str, float], cost: int,
                 category: str, character: Optional[str] = None,
                 extra_effect=None):
        self.name = name
        self.stats = stats or {}
        self.cost = cost
        self.category = category
        self.character = character
        self.extra_effect = extra_effect

    def __repr__(self):
        return f"Item({self.name}, cost={self.cost})"

# -------------------------
# Example extra effect
# -------------------------
def vishkar_condensor_effect(stats):
    hp = stats.get("HP", 0)
    if hp > 100:
        return {"HP": -100, "Shields": 100}
    else:
        return {"HP": -hp, "Shields": hp}

# -------------------------
# Item pool (same as prior)
# -------------------------
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

    Item("Field Rations", {}, cost=1000, category="Survival"),
    Item("Running Shoes", {"HP": 10}, cost=1000, category="Survival"),
    Item("Adrenaline Shot", {"HP": 25}, cost=1500, category="Survival"),
    Item("Armored Vest", {"Armor": 25}, cost=1500, category="Survival"),
    Item("Electrolytes", {}, cost=1500, category="Survival"),
    Item("First Aid Kit", {"Shields": 25}, cost=1500, category="Survival"),
    Item("Heartbeat Sensor", {"Move Speed": 0.05}, cost=1500, category="Survival"),
    Item("Siphon Gloves", {"HP": 25}, cost=1500, category="Survival"),
    Item("Reinforced Titanium", {"Shields": 25}, cost=3750, category="Survival"),
    Item("Cushioned Padding", {"Shields": 25}, cost=4000, category="Survival"),
    Item("Ironclad Exhaust Ports", {"Cooldown Reduction": 0.05}, cost=4000, category="Survival"),
    Item("Vishkar Condensor", {"Shields": 25}, cost=4000, category="Survival", extra_effect=vishkar_condensor_effect),
    Item("Vital-E-Tee", {"Armor": 10}, cost=4000, category="Survival"),
    Item("Crusader Hydraulics", {"Armor": 25, "Damage Reduction": 0.10}, cost=10000, category="Survival"),
    Item("Iron Eyes", {"Shields": 25}, cost=4500, category="Survival"),
    Item("Meka Z-Series", {
        "HP Multiplier": 0.08,
        "Armor Multiplier": 0.08,
        "Shields Multiplier": 0.08,
    }, cost=5000, category="Survival"),
    Item("Geneticist's Vial", {"HP": 25}, cost=9000, category="Survival"),
    Item("Divine Intervention", {"Shields": 50, "Damage Reduction": 0.15}, cost=95000, category="Survival"),
    Item("Gloom Gauntlet", {"Armor": 50, "Melee Damage": 0.15}, cost=10000, category="Survival"),
    Item("Martian Mender", {"HP": 25, "Cooldown Reduction": 0.10}, cost=10000, category="Survival"),
    Item("Phantasmic Flux", {
        "Weapon Power": 0.10,
        "Ability Power": 0.10,
        "Weapon Lifesteal": 0.15,
        "Ability Lifesteal": 0.15
    }, cost=10000, category="Survival"),
    Item("Rustung Von Wilhelm", {
        "HP Multiplier": 0.15,
        "Armor Multiplier": 0.15,
        "Shields Multiplier": 0.15,
        "Damage Reduction": 0.03
    }, cost=10000, category="Survival"),

    # Juno-specific items
    Item("Lock-On Shield", {"Ability Power": 0.1001}, 4000, "Survival", character="Juno"),
    Item("Lux Loop", {"Ability Power": 0.1001}, 4000, "Ability", character="Juno"),
    Item("Pulsar Torpedos", {"Ability Lifesteal": 0.10}, 10000, "Ability", character="Juno",
         extra_effect=lambda stats: 20 * (1 + stats.get("Ability Power", 0.0))),
    Item("Solar Shielding", {"Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Red Promise Regulator", {"Shields": 50, "Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Boosted Rockets", {"Shields": 25}, 4000, "Survival", character="Juno"),
    Item("Forti-Glide", {"Shields": 75, "Damage Reduction": 0.10}, 10000, "Survival", character="Juno"),
    Item("Sunburst Serum", {"Shields": 75}, 10000, "Survival", character="Juno"),
]

# -------------------------
# Base stats & targets
# -------------------------
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

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

# -------------------------
# Stat calculation (cached)
# -------------------------
@st.cache_data(show_spinner=False)
def calculate_build_stats_keyed(item_names: Tuple[str, ...], base_stats: Dict[str, float]) -> Dict[str, float]:
    # Helper to compute stats from a tuple of item names (used in caching)
    items = [next(it for it in ITEM_POOL if it.name == nm) for nm in item_names]
    return calculate_build_stats(items, base_stats)

def calculate_build_stats(items: List[Item], base_stats: Dict[str, float]) -> Dict[str, float]:
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
        "HP Multiplier": 0.0,
        "Armor Multiplier": 0.0,
        "Shields Multiplier": 0.0,
        "Bonus Damage": 0.0,
    }

    for item in items:
        for stat, val in item.stats.items():
            if stat == "Cooldown Reduction":
                stats["Cooldown Reduction"] *= max(0.0, (1.0 - val))
            elif stat in stats:
                stats[stat] += val
            else:
                stats[stat] = stats.get(stat, 0.0) + val

    # generic multipliers
    for key in ["HP Multiplier", "Armor Multiplier", "Shields Multiplier"]:
        mul = stats.get(key, 0.0)
        if mul:
            if key == "HP Multiplier":
                stats["HP"] *= (1.0 + mul)
            elif key == "Armor Multiplier":
                stats["Armor"] *= (1.0 + mul)
            elif key == "Shields Multiplier":
                stats["Shields"] *= (1.0 + mul)

    # special named multipliers
    for item in items:
        if item.name == "Meka Z-Series":
            stats["HP"] *= 1.08
            stats["Armor"] *= 1.08
            stats["Shields"] *= 1.08

    # apply extra_effects
    for item in items:
        if item.extra_effect:
            try:
                out = item.extra_effect(stats.copy())
            except Exception:
                out = None
            if out is None:
                continue
            if isinstance(out, dict):
                for k, v in out.items():
                    stats[k] = stats.get(k, 0.0) + v
            else:
                stats["Bonus Damage"] = stats.get("Bonus Damage", 0.0) + float(out)

    stats["Cooldown Reduction"] = max(stats.get("Cooldown Reduction", 1.0), 0.1)
    stats["Ability Power"] = stats.get("Ability Power", 0.0) * stats["Cooldown Reduction"]

    if any(i.name == "Lock-On Shield" for i in items):
        stats["HP"] += 0.5 * stats.get("Shields", 0.0)

    return stats

# -------------------------
# Evaluation
# -------------------------
def evaluate_build(stats: Dict[str, float], target: str, items: List[Item]) -> float:
    base_damage = 100.0
    ap = stats.get("Ability Power", 0.0)
    bonus = stats.get("Bonus Damage", 0.0)
    if target == "Ability Damage":
        return base_damage * (1.0 + ap) + bonus
    elif target == "Ability DPS":
        base_cooldown = 6.0
        effective_cd = base_cooldown * stats.get("Cooldown Reduction", 1.0)
        total_damage = base_damage * (1.0 + ap) + bonus
        return total_damage / effective_cd if effective_cd > 0 else 0.0
    elif target == "HP":
        return stats.get("HP", 0.0)
    elif target == "Shields":
        return stats.get("Shields", 0.0)
    elif target == "Armor":
        return stats.get("Armor", 0.0)
    elif target == "Total HP":
        return stats.get("HP", 0.0) + stats.get("Shields", 0.0) + stats.get("Armor", 0.0)
    elif target == "Weapon Power":
        return stats.get("Weapon Power", 0.0)
    elif target == "Cooldown Reduction":
        return 1.0 - stats.get("Cooldown Reduction", 1.0)
    elif target == "Weapon DPS":
        return 100.0 * (1.0 + stats.get("Weapon Power", 0.0)) * (1.0 + stats.get("Attack Speed", 0.0)) * (1.0 + stats.get("Reload Speed", 0.0)) * (1.0 + stats.get("Critical Hit Damage", 0.0))
    elif target == "Effective HP":
        total = stats.get("HP", 0.0) + stats.get("Shields", 0.0) + stats.get("Armor", 0.0)
        dr = min(stats.get("Damage Reduction", 0.0), 0.99)
        return total / (1.0 - dr) if (1.0 - dr) > 0 else float('inf')
    else:
        return stats.get(target, 0.0)

# -------------------------
# Filtering helper
# -------------------------
def filter_items_for_target(items: List[Item], target: str) -> List[Item]:
    relevant_stats = target_relevant_stats.get(target, set())
    filtered = []
    for item in items:
        if any(stat in relevant_stats for stat in item.stats.keys()):
            filtered.append(item)
        elif item.name == "Lock-On Shield" and target in {"HP", "Shields", "Effective HP", "Total HP"}:
            filtered.append(item)
    return filtered

# -------------------------
# Search function (top_k)
# -------------------------
def find_best_builds(items: List[Item], base_stats: Dict[str, float], budget: int,
                     target: str, max_items: int, top_k: int = 1, progress_callback=None) -> List[Tuple[float, Tuple[Item, ...]]]:
    items_sorted = sorted(items, key=lambda it: it.cost)
    n = len(items_sorted)
    # single item contributions for optimistic bound
    single_contribs = [evaluate_build(calculate_build_stats([it], base_stats), target, [it]) for it in items_sorted]
    sorted_single_desc = sorted(single_contribs, reverse=True)

    best_results: List[Tuple[float, Tuple[Item, ...]]] = []
    best_score = -float('inf')
    checked = 0
    start_time = time.time()

    from functools import lru_cache
    @lru_cache(maxsize=200000)
    def eval_key(item_names: Tuple[str, ...]) -> float:
        stats = calculate_build_stats_keyed(item_names, base_stats)
        return evaluate_build(stats, target, [])

    def optimistic_bound(current_score: float, remaining_slots: int):
        if remaining_slots <= 0:
            return current_score
        return current_score + sum(sorted_single_desc[:remaining_slots])

    def record_candidate(build_items: Tuple[Item, ...], score: float):
        nonlocal best_results, best_score
        best_results.append((score, build_items))
        best_results.sort(key=lambda x: x[0], reverse=True)
        del best_results[top_k:]
        best_score = best_results[0][0] if best_results else -float('inf')

    def backtrack(start_idx: int, chosen: List[Item], cost_so_far: int):
        nonlocal checked, best_score
        checked += 1
        if progress_callback and checked % 300 == 0:
            elapsed = time.time() - start_time
            progress_callback(checked, elapsed)

        if chosen:
            key = tuple(it.name for it in chosen)
            score = eval_key(key)
            if len(best_results) < top_k or score > best_results[-1][0]:
                record_candidate(tuple(chosen), score)

        if len(chosen) >= max_items:
            return

        remaining_slots = max_items - len(chosen)
        current_score = 0.0
        if chosen:
            current_score = eval_key(tuple(it.name for it in chosen))
        bound = optimistic_bound(current_score, remaining_slots)
        if len(best_results) >= top_k and bound <= best_results[-1][0]:
            return

        for i in range(start_idx, n):
            it = items_sorted[i]
            new_cost = cost_so_far + it.cost
            if new_cost > budget:
                continue
            chosen.append(it)
            backtrack(i + 1, chosen, new_cost)
            chosen.pop()

    backtrack(0, [], 0)
    return best_results

# -------------------------
# UI helpers: item color mapping
# -------------------------
def cost_color_html(item: Item) -> str:
    # user requested: 1000-1500 green; 3750-6000 aqua; >6000 light purple
    c = item.cost
    if 1000 <= c <= 1500:
        color = "#33cc33"  # green
    elif 3750 <= c <= 6000:
        color = "#00cccc"  # aqua
    elif c > 6000:
        color = "#d6b3ff"  # light purple
    else:
        color = "#ffffff"  # default white/black text background
    return f'<span style="color:{color}; font-weight:600">{item.name} (Cost: {item.cost})</span>'

def item_html_list(items: List[Item]) -> str:
    parts = []
    for it in items:
        parts.append(cost_color_html(it) + f' — {it.category} — Stats: {it.stats}')
    return "<br>".join(parts)

# -------------------------
# Display relevant stats
# -------------------------
def display_relevant_stats(stats: Dict[str, float], target: str) -> List[str]:
    relevant_stats = target_relevant_stats.get(target, set())
    lines = []
    for s in ["HP", "Shields", "Armor"]:
        if s in relevant_stats or target in ["Total HP", "Effective HP"]:
            lines.append(f"{s}: {stats.get(s, 0):.1f}")
    for stat in sorted(relevant_stats):
        if stat in ["HP", "Shields", "Armor"]:
            continue
        val = stats.get(stat)
        if val is None:
            continue
        if isinstance(val, float) and abs(val) < 10:
            lines.append(f"{stat}: {val*100:.1f}%")
        else:
            if isinstance(val, float):
                lines.append(f"{stat}: {val:.2f}")
            else:
                lines.append(f"{stat}: {val}")
    return lines

# -------------------------
# Radar chart helper (matplotlib)
# -------------------------
def plot_radar(build_stats_list: List[Dict[str, float]], labels: List[str], stats_to_plot: List[str], title: str = "Build comparison"):
    """
    build_stats_list: list of stats dicts for each build (length = K)
    labels: list of labels for each build
    stats_to_plot: list of stat keys (order matters)
    """
    num_vars = len(stats_to_plot)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    # complete circle
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Normalize each stat across builds to [0,1] so chart is comparative
    # prepare matrix: rows=builds, cols=stats
    values_matrix = []
    for stats in build_stats_list:
        row = [float(stats.get(k, 0.0)) for k in stats_to_plot]
        values_matrix.append(row)
    arr = np.array(values_matrix, dtype=float)
    # avoid dividing by zero: use range (max-min) or 1 if all equal
    mins = arr.min(axis=0)
    maxs = arr.max(axis=0)
    ranges = np.where((maxs - mins) == 0, 1.0, maxs - mins)
    normalized = (arr - mins) / ranges
    for i, row in enumerate(normalized):
        vals = row.tolist()
        vals += vals[:1]
        ax.plot(angles, vals, label=labels[i])
        ax.fill(angles, vals, alpha=0.15)
    ax.set_thetagrids(np.degrees(angles[:-1]), stats_to_plot)
    ax.set_title(title)
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    ax.set_ylim(0, 1)
    st.pyplot(fig)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Build Optimizer v2", layout="wide")
st.title("Game Build Optimizer — Radar + Side-by-side comparison")

col1, col2 = st.columns([1, 2])

with col1:
    character = st.selectbox("Character", list(BASE_STATS.keys()))
    money = st.number_input("Money budget", min_value=0, max_value=500000, value=10000, step=500)
    target = st.selectbox("Optimization target", list(target_relevant_stats.keys()), index=7)
    max_items = st.slider("Max items in a build", 1, 8, 6)
    # User requested: customize up to how many builds are generated
    max_builds_to_generate = st.slider("Generate up to how many builds (Top-K search limit)", 1, 20, 6)
    top_k_show = st.slider("How many top builds to show", 1, max_builds_to_generate, 3)
    st.markdown("**Filters**")
    categories = sorted({it.category for it in ITEM_POOL})
    chosen_categories = st.multiselect("Categories", options=categories, default=categories)
    name_filter = st.text_input("Name filter")
    include_char_only = st.checkbox("Only items for selected character", value=False)
    st.markdown("---")
    st.write("Color legend:")
    st.markdown("- <span style='color:#33cc33;font-weight:600'>Green</span> — cost 1,000–1,500", unsafe_allow_html=True)
    st.markdown("- <span style='color:#00cccc;font-weight:600'>Aqua</span> — cost 3,750–6,000", unsafe_allow_html=True)
    st.markdown("- <span style='color:#d6b3ff;font-weight:600'>Light purple</span> — cost > 6,000", unsafe_allow_html=True)

with col2:
    st.markdown("### Candidate items")
    def item_visible(it: Item) -> bool:
        if chosen_categories and it.category not in chosen_categories:
            return False
        if name_filter and name_filter.lower() not in it.name.lower():
            return False
        if include_char_only and it.character and it.character != character:
            return False
        return True
    filtered_items = [it for it in ITEM_POOL if item_visible(it) and (it.character is None or not include_char_only or it.character == character)]
    filtered_items = filter_items_for_target(filtered_items, target)
    st.write(f"{len(filtered_items)} filtered items")
    for it in filtered_items:
        st.markdown(cost_color_html(it) + f" — {it.category} — Stats: {it.stats}", unsafe_allow_html=True)

if st.button("Generate builds"):
    with st.spinner("Searching..."):
        progress_placeholder = st.empty()
        progress_bar = st.progress(0)
        def progress_cb(checked, extra):
            pct = min(0.95, math.tanh(checked / 2000.0) * 0.99)
            progress_bar.progress(int(pct * 100))
            progress_placeholder.text(f"Checked ~{checked} partial builds — elapsed {extra:.1f}s")

        # get results (limit search to up to max_builds_to_generate during pruning)
        results = find_best_builds(filtered_items, BASE_STATS[character], money, target,
                                   max_items, top_k=max_builds_to_generate, progress_callback=progress_cb)
        progress_bar.progress(100)
        progress_placeholder.text("Search complete")

        if not results:
            st.warning("No builds found.")
        else:
            # Trim to the number user wants to display
            results = results[:top_k_show]
            st.success(f"Showing top {len(results)} builds (generated up to {max_builds_to_generate})")

            # Prepare a list for radar chart and side-by-side DataFrame
            build_labels = []
            build_stats_list = []
            build_scores = []
            df_rows = []
            for rank, (score, build) in enumerate(results, start=1):
                item_list = list(build)
                stats = calculate_build_stats(item_list, BASE_STATS[character])
                total_cost = sum(it.cost for it in item_list)
                build_labels.append(f"Rank {rank} (Cost:{total_cost})")
                build_stats_list.append(stats)
                build_scores.append(score)
                # Flatten relevant stats for DataFrame: include HP, Shields, Armor + top relevant stats for target
                row = {
                    "Rank": rank,
                    "Score": round(score, 3),
                    "Total Cost": total_cost,
                    "Items": ", ".join(it.name for it in item_list)
                }
                # include a few stats so side-by-side is meaningful
                for k in ["HP", "Shields", "Armor", "Ability Power", "Weapon Power", "Attack Speed", "Cooldown Reduction", "Damage Reduction"]:
                    row[k] = round(stats.get(k, 0.0), 4)
                df_rows.append(row)

            df = pd.DataFrame(df_rows).set_index("Rank")

            # Show side-by-side table (interactive)
            st.markdown("### Side-by-side summary")
            st.dataframe(df)

            # Show expanders for each build with items color-coded
            for rank, (score, build) in enumerate(results, start=1):
                total_cost = sum(it.cost for it in build)
                with st.expander(f"Rank {rank} — Score: {score:.3f} — Cost: {total_cost}"):
                    st.markdown(item_html_list(list(build)), unsafe_allow_html=True)
                    stats = calculate_build_stats(list(build), BASE_STATS[character])
                    st.write("Stats breakdown:")
                    for line in display_relevant_stats(stats, target):
                        st.write(line)

            # Radar chart: choose some stats to compare
            # We'll include a small set that tends to be present across many builds
            stats_to_plot = ["HP", "Shields", "Armor", "Ability Power", "Weapon Power", "Attack Speed", "Damage Reduction"]
            st.markdown("### Radar chart comparison")
            plot_radar(build_stats_list, build_labels, stats_to_plot, title=f"Top {len(results)} builds comparison")

        st.balloons()
