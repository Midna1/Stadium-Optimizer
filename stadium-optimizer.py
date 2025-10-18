# streamlit_build_optimizer.py
import streamlit as st
from functools import lru_cache
from itertools import combinations
from typing import List, Dict, Tuple, Optional
import math
import time

# -------------------------
# Item class and utilities
# -------------------------
class Item:
    def __init__(self, name: str, stats: Dict[str, float], cost: int,
                 category: str, character: Optional[str] = None,
                 extra_effect=None):
        self.name = name
        self.stats = stats or {}
        self.cost = cost
        self.category = category  # "Weapon", "Ability", "Survival", etc.
        self.character = character
        self.extra_effect = extra_effect  # function(stats) -> dict or value

    def __repr__(self):
        return f"Item({self.name}, cost={self.cost})"

# ---- Extra effect example (already in original) ----
def vishkar_condensor_effect(stats):
    hp = stats.get("HP", 0)
    if hp > 100:
        return {"HP": -100, "Shields": 100}
    else:
        return {"HP": -hp, "Shields": hp}

# -------------------------
# Item pool (kept from user, minor fix for lambda)
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
    # NOTE: original lambda returned numeric; here we accept numeric or dict in code.
    Item("Pulsar Torpedos", {"Ability Lifesteal": 0.10}, 10000, "Ability", character="Juno",
         extra_effect=lambda stats: 20 * (1 + stats.get("Ability Power", 0.0))),
    Item("Solar Shielding", {"Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Red Promise Regulator", {"Shields": 50, "Ability Power": 0.15}, 10000, "Ability", character="Juno"),
    Item("Boosted Rockets", {"Shields": 25}, 4000, "Survival", character="Juno"),
    Item("Forti-Glide", {"Shields": 75, "Damage Reduction": 0.10}, 10000, "Survival", character="Juno"),
    Item("Sunburst Serum", {"Shields": 75}, 10000, "Survival", character="Juno"),
]

# -------------------------
# Base stats and targets
# -------------------------
BASE_STATS = {
    "Juno": {"HP": 75, "Shields": 150, "Armor": 0},
    "Kiriko": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mercy": {"HP": 225, "Shields": 0, "Armor": 0},
    "Mei": {"HP": 300, "Shields": 0, "Armor": 0},
}

# What stats matter for each optimization target
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
# Core stat calculation
# -------------------------
def calculate_build_stats(items: List[Item], base_stats: Dict[str, float]) -> Dict[str, float]:
    """Return a stats dictionary after applying items. Fully applies extra_effects and multipliers."""
    # Start from base
    stats = {
        "HP": base_stats.get("HP", 0),
        "Shields": base_stats.get("Shields", 0),
        "Armor": base_stats.get("Armor", 0),
        "Max Ammo": 0,
        "Weapon Power": 0.0,
        "Ability Power": 0.0,
        "Attack Speed": 0.0,
        "Reload Speed": 0.0,
        # NOTE: store cooldown multiplicatively (1.0 = no reduction; multiply by (1 - val) for each)
        "Cooldown Reduction": 1.0,
        "Damage Reduction": 0.0,
        "Weapon Lifesteal": 0.0,
        "Ability Lifesteal": 0.0,
        "Move Speed": 0.0,
        "Melee Damage": 0.0,
        "Critical Hit Damage": 0.0,
        # Multipliers that items may add
        "HP Multiplier": 0.0,
        "Armor Multiplier": 0.0,
        "Shields Multiplier": 0.0,
        # extra arbitrary fields
        "Bonus Damage": 0.0,
    }

    # 1) Add flat stats and multiplicative cooldown modifiers
    for item in items:
        for stat, val in item.stats.items():
            if stat == "Cooldown Reduction":
                # item provides "Cooldown Reduction": 0.05 meaning -5% cooldown
                stats["Cooldown Reduction"] *= max(0.0, (1.0 - val))
            elif stat in stats:
                stats[stat] += val
            else:
                # unknown stat: add it anyway
                stats[stat] = stats.get(stat, 0.0) + val

    # 2) Apply explicit multiplier items (by name) and generic multiplier keys
    # Apply generic multipliers from item.stats (HP Multiplier keys etc.)
    for key in ["HP Multiplier", "Armor Multiplier", "Shields Multiplier"]:
        mul = stats.get(key, 0.0)
        if mul:
            if key == "HP Multiplier":
                stats["HP"] *= (1.0 + mul)
            elif key == "Armor Multiplier":
                stats["Armor"] *= (1.0 + mul)
            elif key == "Shields Multiplier":
                stats["Shields"] *= (1.0 + mul)

    # Also support item-by-name special multipliers
    for item in items:
        if item.name == "Meka Z-Series":
            stats["HP"] *= 1.08
            stats["Armor"] *= 1.08
            stats["Shields"] *= 1.08

    # 3) Apply extra_effect from items. The extra_effect may return a dict or a single numeric value
    # If a number is returned, interpret as BonusDamage (backward-compatible with original lambda).
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
                # numeric -> store as Bonus Damage
                stats["Bonus Damage"] = stats.get("Bonus Damage", 0.0) + float(out)

    # 4) Final adjustments and clamps
    # Clamp cooldown reduction so that it's not absurdly small (set a lower cap at 0.1 -> 90% reduction cap)
    stats["Cooldown Reduction"] = max(stats.get("Cooldown Reduction", 1.0), 0.1)
    # Apply cooldown reduction effect to ability power (original logic: AP * cooldown)
    stats["Ability Power"] = stats.get("Ability Power", 0.0) * stats["Cooldown Reduction"]

    # 5) Lock-On Shield effect (50% of shields converted to extra HP)
    if any(i.name == "Lock-On Shield" for i in items):
        stats["HP"] += 0.5 * stats.get("Shields", 0.0)

    return stats

# -------------------------
# Evaluation functions
# -------------------------
def evaluate_build(stats: Dict[str, float], target: str, items: List[Item]) -> float:
    """Return a numeric score for a build according to target."""
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
# Filtering helpers
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
# Search (backtracking with pruning + caching)
# -------------------------
def find_best_builds(items: List[Item], base_stats: Dict[str, float], budget: int,
                     target: str, max_items: int, top_k: int = 1, progress_callback=None) -> List[Tuple[float, Tuple[Item, ...]]]:
    """
    Find top-k builds using backtracking with simple pruning and caching.
    Returns list of (score, build_tuple) sorted descending by score.
    progress_callback(optional): func(checked_count, total_estimate) for UI progress.
    """
    # Pre-sort items by cost ascending to help pruning
    items_sorted = sorted(items, key=lambda it: it.cost)
    n = len(items_sorted)

    # Precompute single-item contributions for a cheap optimistic upper bound
    single_contribs = []
    for it in items_sorted:
        stats = calculate_build_stats([it], base_stats)
        single_contribs.append(evaluate_build(stats, target, [it]))

    # For optimistic bound of remaining items, we will use the best possible single-item contributions
    sorted_single_contribs_desc = sorted(single_contribs, reverse=True)

    best_results: List[Tuple[float, Tuple[Item, ...]]] = []
    best_score = -float('inf')
    checked = 0
    start_time = time.time()
    cache: Dict[Tuple[Tuple[str, ...], str], float] = {}

    def record_candidate(build_items: Tuple[Item, ...], score: float):
        nonlocal best_score, best_results
        # insert maintaining top_k sorted descending
        best_results.append((score, build_items))
        best_results.sort(key=lambda x: x[0], reverse=True)
        # keep only top_k
        del best_results[top_k:]
        best_score = best_results[0][0] if best_results else -float('inf')

    # simple optimistic bound function: current score + sum of best single-item contributions for remaining slots
    def optimistic_bound(current_score: float, remaining_slots: int):
        if remaining_slots <= 0:
            return current_score
        return current_score + sum(sorted_single_contribs_desc[:remaining_slots])

    # memoized eval for a given set of items by names and char (string key)
    @lru_cache(maxsize=100000)
    def eval_for_key(item_names_key: Tuple[str, ...], character_key: str) -> float:
        key_items = tuple(next(it for it in items_sorted if it.name == nm) for nm in item_names_key)
        stats = calculate_build_stats(list(key_items), base_stats)
        return evaluate_build(stats, target, list(key_items))

    # backtracking
    def backtrack(start_idx: int, chosen: List[Item], cost_so_far: int):
        nonlocal checked, best_score
        # progress callback
        checked += 1
        if progress_callback and checked % 500 == 0:
            elapsed = time.time() - start_time
            progress_callback(checked, elapsed)

        # Evaluate current build
        if chosen:
            key = tuple(it.name for it in chosen)
            # use cached eval
            score = eval_for_key(tuple(key), "")
            # Update best
            if score > best_score or len(best_results) < top_k:
                record_candidate(tuple(chosen), score)

        # If reached max items, stop deeper recursion
        if len(chosen) >= max_items:
            return

        # For each candidate item index >= start_idx
        remaining_slots = max_items - len(chosen)
        # Compute optimistic upper bound for pruning:
        # current best possible = current evaluated score (or 0) + sum of best remaining single-item contributions
        current_score = 0.0
        if chosen:
            current_score = eval_for_key(tuple(it.name for it in chosen), "")

        bound = optimistic_bound(current_score, remaining_slots)
        # If bound not better than current best, prune
        if len(best_results) >= top_k and bound <= best_results[-1][0]:
            return

        for i in range(start_idx, n):
            it = items_sorted[i]
            new_cost = cost_so_far + it.cost
            if new_cost > budget:
                # since sorted by cost ascending, any further items will also be too expensive at this index (but combination might allow different cheaper items)
                continue
            chosen.append(it)
            backtrack(i + 1, chosen, new_cost)
            chosen.pop()

    # Start backtracking
    backtrack(0, [], 0)
    return best_results

# -------------------------
# Display helpers
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
        # present small fractions as percentages
        if isinstance(val, float) and abs(val) < 10:
            lines.append(f"{stat}: {val * 100:.1f}%")
        else:
            # float large numbers formatting
            if isinstance(val, float):
                lines.append(f"{stat}: {val:.2f}")
            else:
                lines.append(f"{stat}: {val}")
    return lines

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Game Build Optimizer", layout="wide")
st.title("Game Build Optimizer — improved")

col_left, col_right = st.columns([1, 2])

with col_left:
    character = st.selectbox("Choose your character", list(BASE_STATS.keys()))
    money = st.number_input("Enter your money budget", min_value=0, max_value=500000, value=10000, step=500)

    target = st.selectbox("Choose optimization target", list(target_relevant_stats.keys()), index=7)  # default to Ability DPS

    # Filters: categories and name search
    categories = sorted({it.category for it in ITEM_POOL})
    chosen_categories = st.multiselect("Categories to include", options=categories, default=categories)

    name_filter = st.text_input("Item name filter (substring, optional)")

    # max items, top-k, cost cap per item
    max_items = st.slider("Maximum number of items to buy", 1, 8, 6)
    top_k = st.number_input("Show top K builds", min_value=1, max_value=20, value=3, step=1)
    max_cost_per_item = st.number_input("Maximum cost per item (0 = no limit)", min_value=0, value=0)

    # optional: narrow to character-specific items or global
    include_character_only = st.checkbox("Only show items for selected character (hide others)", value=False)

    st.markdown("---")
    st.write("Extra options")
    show_progress = st.checkbox("Show search progress", value=True)
    limit_search_items = st.slider("Limit number of candidate items (for speed)", 5, min(20, len(ITEM_POOL)), value=min(40, len(ITEM_POOL)))

    # Weights: allow user to add a weight modifier for multi-importance evaluation (applies to the final score)
    st.markdown("### Optional stat weighting (advanced)")
    weight_target = st.number_input(f"Weight multiplier for primary target ({target})", min_value=0.0, value=1.0, step=0.1)

with col_right:
    st.markdown("### Candidate Items")
    # Filter items by character and category and name
    filtered_items = [
        it for it in ITEM_POOL
        if (it.character is None or not include_character_only or it.character == character or not include_character_only)
    ]
    # second pass: respect chosen_categories and name_filter and character applicability
    def item_visible(it: Item) -> bool:
        if chosen_categories and it.category not in chosen_categories:
            return False
        if name_filter and name_filter.lower() not in it.name.lower():
            return False
        # hide items for other characters unless include_character_only is False
        if include_character_only and it.character and it.character != character:
            return False
        if max_cost_per_item > 0 and it.cost > max_cost_per_item:
            return False
        return True

    filtered_items = [it for it in ITEM_POOL if item_visible(it) and (it.character is None or it.character == character or not include_character_only)]

    # Further filter by "relevant to target" to reduce search space
    filtered_items = filter_items_for_target(filtered_items, target)

    # Option: limit list for performance (take most promising items by simple per-cost heuristic)
    if len(filtered_items) > limit_search_items:
        # score items by simple per-cost contribution to the target (single-item eval / cost)
        contributions = []
        for it in filtered_items:
            s = calculate_build_stats([it], BASE_STATS[character])
            contrib = evaluate_build(s, target, [it])
            efficiency = contrib / (it.cost + 1)
            contributions.append((efficiency, it))
        contributions.sort(key=lambda x: x[0], reverse=True)
        filtered_items = [it for _, it in contributions[:limit_search_items]]

    st.write(f"{len(filtered_items)} items will be considered for the search (budget: {money})")
    # show a compact table
    for it in filtered_items:
        st.write(f"- {it.name} — {it.category} — Cost: {it.cost} — Stats: {it.stats}")

# -------------------------
# Run search (button)
# -------------------------
run_search = st.button("Find best builds")

if run_search:
    with st.spinner("Searching for best builds..."):
        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        def progress_cb(checked, extra):
            # update a simple progress bar based on elapsed time heuristic (not a total progress)
            # we do not promise accuracy; just provide feel of progress.
            # map checked to a squashed progress percentage
            pct = min(0.98, math.tanh(checked / 2000.0) * 0.99)
            try:
                progress_bar.progress(int(pct * 100))
                status_placeholder.text(f"Checked ~{checked} partial builds, elapsed {extra:.1f}s")
            except Exception:
                pass

        # Kick off search
        search_start = time.time()
        results = find_best_builds(filtered_items, BASE_STATS[character], money,
                                   target, max_items, top_k=top_k,
                                   progress_callback=(progress_cb if show_progress else None))
        search_time = time.time() - search_start
        progress_bar.progress(100)
        status_placeholder.text(f"Search done — examined builds in {search_time:.2f}s.")

        if not results:
            st.warning("No valid build found within budget / filters.")
        else:
            # Show results
            st.success(f"Found {len(results)} build(s).")
            for rank, (score, build) in enumerate(results, start=1):
                # Recompute stats to display
                stats = calculate_build_stats(list(build), BASE_STATS[character])
                adjusted_score = score * weight_target  # apply optional weighting
                with st.expander(f"Rank #{rank} — Score: {adjusted_score:.3f} — Cost: {sum(it.cost for it in build)}"):
                    st.write("Items:")
                    for it in build:
                        st.write(f"- {it.name} (Cost: {it.cost}) — {it.stats} {'[char: '+it.character+']' if it.character else ''}")
                    st.write("Stats breakdown:")
                    for line in display_relevant_stats(stats, target):
                        st.write(line)
                    # Show raw important stats
                    st.write(f"Raw score (unweighted): {score:.3f}")
                    st.write(f"Weighted score: {adjusted_score:.3f}")
                    # small table style display of whole stats dict
                    st.table({k: (f"{v:.3f}" if isinstance(v, float) else v) for k, v in sorted(stats.items())})

        st.balloons()

# -------------------------
# Notes and tips
# -------------------------
st.markdown("---")
st.markdown(
    """
**Notes & Implementation details**
- Search uses a backtracking approach with a simple optimistic bound + memoized evaluations, which usually prunes many combinations.
- `extra_effect` functions are now supported; they may return either a `dict` of stat changes or a single numeric (treated as *Bonus Damage* for backward compatibility).
- You can speed up search by decreasing `max_items`, limiting candidate items, or tuning filters.
- If you need *exact exhaustive* search for large candidate sets, consider a cloud worker or more advanced pruning heuristics (ILP/knapsack-style).
"""
)
