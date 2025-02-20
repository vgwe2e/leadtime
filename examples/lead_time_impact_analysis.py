"""
Analyze impact of lead time changes for specific network constraints.
"""

import numpy as np
import matplotlib.pyplot as plt
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.simulation import MonteCarloSimulation

# Network Parameters
BASE_LEAD_TIME = 3  # average network lead time
UNLOAD_TIME = 1    # constant unload time
LEAD_TIMES = [3, 5, 6, 12]  # specified lead times including inspection
COVERAGE_DAYS = 7  # base safety stock coverage

# Simulation Parameters
MEAN_DEMAND = 100  # units per day
DEMAND_STD = 20    # 20% variability
SIMULATION_DAYS = 90
ITERATIONS = 1000

# Create simulation
demand_gen = DemandGenerator(mean=MEAN_DEMAND, std_dev=DEMAND_STD, seed=42)
simulation = MonteCarloSimulation(demand_gen, iterations=ITERATIONS)

# Run simulation
results = simulation.simulate_safety_stock(
    coverage_days=COVERAGE_DAYS,
    simulation_days=SIMULATION_DAYS,
    lead_times=[lt + UNLOAD_TIME for lt in LEAD_TIMES]  # Add unload time
)

# Analyze results
stats = simulation.analyze_results(results)
confidence_intervals = simulation.calculate_confidence_intervals(results)

# Print Analysis
print("\nLead Time Impact Analysis")
print("-" * 50)
print(f"Base Network Lead Time: {BASE_LEAD_TIME} days")
print(f"Unload Time: {UNLOAD_TIME} day")
print(f"Base Safety Stock Coverage: {COVERAGE_DAYS} days")
print(f"Mean Daily Demand: {MEAN_DEMAND} units")

print("\nSafety Stock Requirements:")
print("-" * 50)

baseline_stock = None
for lt in LEAD_TIMES:
    total_lt = lt + UNLOAD_TIME
    lt_stats = stats[total_lt]
    ci_lower, ci_upper = confidence_intervals[total_lt]
    
    if lt == BASE_LEAD_TIME:
        baseline_stock = lt_stats['mean']
    
    print(f"\nLead Time Scenario: {lt} days (+{UNLOAD_TIME} day unload)")
    print(f"Total Lead Time: {total_lt} days")
    print(f"Safety Stock Required: {lt_stats['mean']:.0f} units")
    print(f"95% CI: [{ci_lower:.0f}, {ci_upper:.0f}]")
    
    if baseline_stock:
        change = lt_stats['mean'] - baseline_stock
        percent_change = (change / baseline_stock) * 100
        print(f"Change from baseline: {change:+.0f} units ({percent_change:+.1f}%)")

# Calculate value impact
print("\nValue Impact Analysis")
print("-" * 50)
inventory_cost_rate = 0.20  # 20% annual holding cost
unit_cost = 50  # example unit cost

for lt in LEAD_TIMES:
    if lt != BASE_LEAD_TIME:
        total_lt = lt + UNLOAD_TIME
        stock_change = stats[total_lt]['mean'] - baseline_stock
        value_impact = stock_change * unit_cost
        annual_cost_impact = value_impact * inventory_cost_rate
        
        print(f"\nLead Time {lt} days vs Baseline:")
        print(f"Additional Inventory Value: ${value_impact:,.0f}")
        print(f"Annual Holding Cost Impact: ${annual_cost_impact:,.0f}")

# Visualization
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plot_data = [(lt, stats[lt + UNLOAD_TIME]['mean']) for lt in LEAD_TIMES]
lts, means = zip(*plot_data)
plt.plot(lts, means, marker='o')
plt.title('Safety Stock vs Lead Time')
plt.xlabel('Lead Time (days)')
plt.ylabel('Safety Stock (units)')
plt.grid(True)

plt.subplot(1, 2, 2)
changes = [(lt, (stats[lt + UNLOAD_TIME]['mean'] - baseline_stock) / baseline_stock * 100)
           for lt in LEAD_TIMES if lt != BASE_LEAD_TIME]
change_lts, change_pcts = zip(*changes)
plt.bar(change_lts, change_pcts)
plt.title('% Change from Baseline')
plt.xlabel('Lead Time (days)')
plt.ylabel('% Change in Safety Stock')
plt.grid(True)

plt.tight_layout()
plt.show()

# Recommendation
print("\nRecommendation:")
print("-" * 50)
max_impact = max([abs(stats[lt + UNLOAD_TIME]['mean'] - baseline_stock) for lt in LEAD_TIMES if lt != BASE_LEAD_TIME])
max_value_impact = max_impact * unit_cost * inventory_cost_rate

if max_value_impact > 10000:  # threshold for significance
    print("TRACK: Lead time changes have significant impact on inventory costs")
    print(f"Maximum annual cost impact: ${max_value_impact:,.0f}")
    print("Recommended actions:")
    print("1. Implement regular lead time monitoring")
    print("2. Focus on scenarios with >5 day variations")
    print("3. Consider automated tracking system")
else:
    print("LOW IMPACT: Lead time tracking may not justify the effort")
    print(f"Maximum annual cost impact: ${max_value_impact:,.0f}")
    print("Recommended actions:")
    print("1. Implement quarterly review instead of continuous tracking")
    print("2. Focus on major network changes only")
    print("3. Use simple spreadsheet tracking") 