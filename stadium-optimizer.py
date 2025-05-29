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

# --- Updated item pool with real items ---
ITEM_POOL = [
    Item("Charged Plating", {"Armor": 25, "Ability Power": 0.10}, cost=1000, category="Ability"),
    Item("Shady Spectacles", {"Ability Lifesteal": 0.10}, cost=1000, category="Ability"),
    Item("Winning Attitude", {"HP": 25}, cost=1500, category="Ability"),
    Item("Custom Stock", {"Weapon Power": 0.05, "Ability Power": 0.10}, cost=3750, category="Ability"),
    Item("Biolight Overflow", {"HP": 25, "Ability Power": 0.05}, cost=4000, category="Ability"),
    Item("Energized Bracers", {"Ability Power": 0.10, "Ability Lifesteal": 0.10}, cost=4000, category="Ability"),
    Item("Junker Whatchamajig", {}, cost=4000, category="Ability"),
    Item("Wrist Wraps", {"Ability Power": 0.05, "Attack Speed": 0.10}, cost=4000, category="Ability"),
    Item("Multi-Tool", {"Ability Power": 0.10, "Cooldown Reduction": 0.05}, cost=45000, category="Ability"),
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
