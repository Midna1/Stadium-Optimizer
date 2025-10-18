# streamlit_build_optimizer_plotly.py
import streamlit as st
from functools import lru_cache
from typing import List, Dict, Tuple, Optional
import math
import time
import heapq
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
# Item pool (kept same)
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
# Stat calculation (cacheable)
# -------------------------
@st.cache_data(show_spinner=False)
def calculate_build_stats_keyed(item_names: Tuple[str, ...], base_stats: Dict[str, float]) -> Dict[str, float]:
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

    # item-by-name multipliers
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
# Search (top-K via backtracking + pruning)
# -------------------------
def find_best_builds(items: List[Item], base_stats: Dict[str, float], budget: int,
                     target: str, max_items: int, top_k_limit: int = 5, progress_callback=None) -> List[Tuple[float, Tuple[Item, ...]]]:
    items_sorted = sorted(items, key=lambda it: it.cost)
    n = len(items_sorted)

    # single item optimistic contributions
    single_contribs = [evaluate_build(calculate_build_stats([it], base_stats), target, [it]) for it in items_sorted]
    sorted_single_desc = sorted(single_contribs, reverse=True)

    # min-heap for top_k (store negative score for max behavior) or store as (score, build)
    top_heap: List[Tuple[float, Tuple[Item, ...]]] = []  # will be min-heap by score

    checked = 0
    start_time = time.time()

    @lru_cache(maxsize=200000)
    def eval_for_key(item_names: Tuple[str, ...]) -> float:
        stats = calculate_build_stats_keyed(item_names, base_stats)
        return evaluate_build(stats, target, [])

    def optimistic_bound(current_score: float, remaining_slots: int):
        if remaining_slots <= 0:
            return current_score
        return current_score + sum(sorted_single_desc[:remaining_slots])

    def record_candidate(build_items: Tuple[Item, ...], score: float):
        # maintain min-heap of size up to top_k_limit
        if len(top_heap) < top_k_limit:
            heapq.heappush(top_heap, (score, build_items))
        else:
            # if score better than smallest in heap, replace
            if score > top_heap[0][0]:
                heapq.heapreplace(top_heap, (score, build_items))

    def backtrack(start_idx: int, chosen: List[Item], cost_so_far: int):
        nonlocal checked
        checked += 1
        if progress_callback and checked % 300 == 0:
            progress_callback(checked, time.time() - start_time)

        if chosen:
            key = tuple(it.name for it in chosen)
            score = eval_for_key(key)
            # If we haven't filled top heap or this score might be good, record
            if len(top_heap) < top_k_limit or score > top_heap[0][0]:
                record_candidate(tuple(chosen), score)

        if len(chosen) >= max_items:
            return

        remaining_slots = max_items - len(chosen)
        current_score = 0.0
        if chosen:
            current_score = eval_for_key(tuple(it.name for it in chosen))
        bound = optimistic_bound(current_score, remaining_slots)
        # If our current optimistic bound can't beat the worst in top_heap, prune
        if top_heap and len(top_heap) >= top_k_limit and bound <= top_heap[0][0]:
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
    # Convert heap to sorted list desc
    results = sorted(top_heap, key=lambda x: x[0], reverse=True)
    return results

# -------------------------
# UI helpers: cost color & html formatting
# -------------------------
def cost_color_html(item: Item) -> str:
    # 1000-1500 green; 3750-6000 aqua; >6000 light purple
    c = item.cost
    if 1000 <= c <= 1500:
        color = "#33cc33"  # green
    elif 3750 <= c <= 6000:
        color = "#00cccc"  # aqua
    elif c > 6000:
        color = "#d6b3ff"  # light purple
    else:
        color = "#000000"  # default black
    return f'<span style="color:{color}; font-weight:700">{item.name} (Cost: {item.cost})</span>'

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
# Plotly radar chart helper
# -------------------------
def plotly_radar(build_stats_list: List[Dict[str, float]], labels: List[str], stats_to_plot: List[str], title: str = "Build comparison"):
    # Build a DataFrame of values
    df = pd.DataFrame([{k: b.get(k, 0.0) for k in stats_to_plot} for b in build_stats_list], index=labels)

    # Normalize per-stat across builds for fair radar comparison
    mins = df.min(axis=0)
    maxs = df.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0
    df_norm = (df - mins) / ranges

    fig = go.Figure()
    for label in df_norm.index:
        values = df_norm.loc[label].tolist()
        # close the loop
        values += values[:1]
        categories = stats_to_plot + [stats_to_plot[0]]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=label,
            hoverinfo='text',
            text=[f"{cat}: {df.loc[label, cat]:.3f}" for cat in stats_to_plot] + [""],
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
        title=title,
        margin=dict(l=40, r=40, t=60, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Build Optimizer (Plotly)", layout="wide")
st.title("Game Build Optimizer — Plotly Radar + Side-by-side")

left, right = st.columns([1, 2])

with left:
    character = st.selectbox("Character", list(BASE_STATS.keys()))
    money = st.number_input("Money budget", min_value=0, max_value=500000, value=10000, step=500)
    target = st.selectbox("Optimization target", list(target_relevant_stats.keys()), index=7)
    max_items = st.slider("Max items in a build", 1, 8, 6)
    max_builds_to_generate = st.slider("Generate up to how many builds (search limit)", 1, 30, 10)
    top_k_show = st.slider("How many top builds to show", 1, max_builds_to_generate, 5)
    st.markdown("**Filters**")
    categories = sorted({it.category for it in ITEM_POOL})
    chosen_categories = st.multiselect("Categories", options=categories, default=categories)
    name_filter = st.text_input("Name filter (substring)")
    include_char_only = st.checkbox("Only items for selected character", value=False)
    st.markdown("---")
    st.markdown("**Color legend** (items shown in build expanders):")
    st.markdown("- <span style='color:#33cc33;font-weight:700'>Green</span> — cost 1,000–1,500", unsafe_allow_html=True)
    st.markdown("- <span style='color:#00cccc;font-weight:700'>Aqua</span> — cost 3,750–6,000", unsafe_allow_html=True)
    st.markdown("- <span style='color:#d6b3ff;font-weight:700'>Light purple</span> — cost > 6,000", unsafe_allow_html=True)

with right:
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
    st.write(f"{len(filtered_items)} filtered items (relevant to target)")

    for it in filtered_items:
        st.markdown(cost_color_html(it) + f" — {it.category} — Stats: {it.stats}", unsafe_allow_html=True)

if st.button("Generate builds"):
    with st.spinner("Searching best builds..."):
        progress_placeholder = st.empty()
        progress_bar = st.progress(0)

        def progress_cb(checked, elapsed):
            pct = min(0.95, math.tanh(checked / 2000.0) * 0.99)
            progress_bar.progress(int(pct * 100))
            progress_placeholder.text(f"Checked ~{checked} partial builds — elapsed {elapsed:.1f}s")

        # Run search - generate up to `max_builds_to_generate` candidate builds
        results = find_best_builds(filtered_items, BASE_STATS[character], money, target,
                                   max_items, top_k_limit=max_builds_to_generate, progress_callback=progress_cb)
        progress_bar.progress(100)
        progress_placeholder.text("Search complete.")

        if not results:
            st.warning("No builds found under those constraints.")
        else:
            # results is list of (score, build) sorted desc already
            results = results[:top_k_show]
            st.success(f"Showing top {len(results)} builds (searched up to {max_builds_to_generate}).")

            # Prepare data for table + radar
            labels = []
            build_stats_list = []
            rows = []
            for idx, (score, build) in enumerate(results, start=1):
                build_items = list(build)
                stats = calculate_build_stats(build_items, BASE_STATS[character])
                total_cost = sum(it.cost for it in build_items)
                label = f"Build #{idx} (Cost:{total_cost})"
                labels.append(label)
                build_stats_list.append(stats)
                rows.append({
                    "Build": label,
                    "Score": round(score, 4),
                    "Total Cost": total_cost,
                    "Items": ", ".join(it.name for it in build_items),
                    "HP": round(stats.get("HP", 0.0), 4),
                    "Shields": round(stats.get("Shields", 0.0), 4),
                    "Armor": round(stats.get("Armor", 0.0), 4),
                    "Ability Power": round(stats.get("Ability Power", 0.0), 6),
                    "Weapon Power": round(stats.get("Weapon Power", 0.0), 6),
                    "Attack Speed": round(stats.get("Attack Speed", 0.0), 6),
                    "Cooldown Reduction": round(1.0 - stats.get("Cooldown Reduction", 1.0), 6),
                    "Damage Reduction": round(stats.get("Damage Reduction", 0.0), 6),
                })

            df = pd.DataFrame(rows).set_index("Build")
            st.markdown("### Side-by-side summary")
            st.dataframe(df)

            # Build expanders with color-coded item lists
            for i, (score, build) in enumerate(results, start=1):
                total_cost = sum(it.cost for it in build)
                with st.expander(f"Build #{i} — Score: {score:.4f} — Cost: {total_cost}"):
                    st.markdown(item_html_list(list(build)), unsafe_allow_html=True)
                    st.write("Stats breakdown:")
                    stats = calculate_build_stats(list(build), BASE_STATS[character])
                    for line in display_relevant_stats(stats, target):
                        st.write(line)

            # Radar chart — default stat set (you can customize if you want)
            stats_to_plot = ["HP", "Shields", "Armor", "Ability Power", "Weapon Power", "Attack Speed", "Damage Reduction"]
            st.markdown("### Radar chart comparison (normalized per-stat)")
            plotly_radar(build_stats_list, labels, stats_to_plot, title=f"Top {len(results)} builds comparison")

        st.balloons()
