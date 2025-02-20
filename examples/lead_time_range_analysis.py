"""
Analyze impact of different ranges of lead time variation.
"""

import numpy as np
import matplotlib.pyplot as plt
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.simulation import MonteCarloSimulation

# Base Parameters
BASE_LT = 3
UNLOAD_TIME = 1
COVERAGE_DAYS = 7
MEAN_DEMAND = 100
DEMAND_STD = 20

# Define variation ranges
SMALL_VARIATION = range(1, 3)    # 1-2 days
MEDIUM_VARIATION = range(3, 5)   # 3-4 days
LARGE_VARIATION = range(9, 11)   # 9-10 days

# Setup simulation
demand_gen = DemandGenerator(mean=MEAN_DEMAND, std_dev=DEMAND_STD, seed=42)
simulation = MonteCarloSimulation(demand_gen, iterations=1000)

# Calculate baseline first
baseline_results = simulation.simulate_safety_stock(
    coverage_days=COVERAGE_DAYS,
    simulation_days=90,
    lead_times=[BASE_LT + UNLOAD_TIME]
)
baseline_stats = simulation.analyze_results(baseline_results)
BASELINE_STOCK = baseline_stats[BASE_LT + UNLOAD_TIME]['mean']

def analyze_variation_range(base_lt, variations):
    """Analyze impact of a range of variations from base lead time."""
    lead_times = [base_lt + var for var in variations]
    results = simulation.simulate_safety_stock(
        coverage_days=COVERAGE_DAYS,
        simulation_days=90,
        lead_times=[lt + UNLOAD_TIME for lt in lead_times]
    )
    stats = simulation.analyze_results(results)
    
    impacts = []
    for lt in lead_times:
        total_lt = lt + UNLOAD_TIME
        change = stats[total_lt]['mean'] - BASELINE_STOCK
        percent_change = (change / BASELINE_STOCK) * 100
        value_impact = change * 50  # $50 per unit
        annual_cost = value_impact * 0.20  # 20% holding cost
        
        impacts.append({
            'variation': lt - base_lt,
            'stock_change': change,
            'percent_change': percent_change,
            'annual_cost': annual_cost
        })
    
    return impacts

# Print baseline
print("\nBaseline Analysis")
print("-" * 50)
print(f"Base Lead Time: {BASE_LT} days (+{UNLOAD_TIME} day unload)")
print(f"Base Safety Stock: {BASELINE_STOCK:.0f} units")

# Analyze each range
print("\nImpact Analysis by Variation Range")
print("-" * 50)

print("\nSMALL VARIATIONS (1-2 days)")
print("-" * 30)
small_impacts = analyze_variation_range(BASE_LT, SMALL_VARIATION)
for impact in small_impacts:
    print(f"+{impact['variation']} days variation:")
    print(f"  Stock Change: {impact['stock_change']:+.0f} units ({impact['percent_change']:+.1f}%)")
    print(f"  Annual Cost Impact: ${impact['annual_cost']:,.0f}")

print("\nMEDIUM VARIATIONS (3-4 days)")
print("-" * 30)
medium_impacts = analyze_variation_range(BASE_LT, MEDIUM_VARIATION)
for impact in medium_impacts:
    print(f"+{impact['variation']} days variation:")
    print(f"  Stock Change: {impact['stock_change']:+.0f} units ({impact['percent_change']:+.1f}%)")
    print(f"  Annual Cost Impact: ${impact['annual_cost']:,.0f}")

print("\nLARGE VARIATIONS (9-10 days)")
print("-" * 30)
large_impacts = analyze_variation_range(BASE_LT, LARGE_VARIATION)
for impact in large_impacts:
    print(f"+{impact['variation']} days variation:")
    print(f"  Stock Change: {impact['stock_change']:+.0f} units ({impact['percent_change']:+.1f}%)")
    print(f"  Annual Cost Impact: ${impact['annual_cost']:,.0f}")

# Visualization
plt.figure(figsize=(10, 6))
variations = []
costs = []

for impacts in [small_impacts, medium_impacts, large_impacts]:
    for impact in impacts:
        variations.append(impact['variation'])
        costs.append(impact['annual_cost'])

plt.bar(variations, costs)
plt.axhline(y=5000, color='r', linestyle='--', label='Significant Impact Threshold')
plt.title('Annual Cost Impact by Lead Time Variation')
plt.xlabel('Days Added to Base Lead Time')
plt.ylabel('Annual Cost Impact ($)')
plt.legend()
plt.grid(True)
plt.show()

# Key Findings
print("\nKEY FINDINGS")
print("-" * 50)
print("1. Small Variations (1-2 days):")
avg_small = np.mean([i['annual_cost'] for i in small_impacts])
print(f"   Average Annual Impact: ${avg_small:,.0f}")
print("   Recommendation: Quarterly review sufficient")

print("\n2. Medium Variations (3-4 days):")
avg_medium = np.mean([i['annual_cost'] for i in medium_impacts])
print(f"   Average Annual Impact: ${avg_medium:,.0f}")
print("   Recommendation: Monthly monitoring recommended")

print("\n3. Large Variations (9-10 days):")
avg_large = np.mean([i['annual_cost'] for i in large_impacts])
print(f"   Average Annual Impact: ${avg_large:,.0f}")
print("   Recommendation: Continuous tracking essential") 