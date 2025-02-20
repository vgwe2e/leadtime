"""
Analyze the impact of lead time changes on safety stock requirements.
"""

import numpy as np
import matplotlib.pyplot as plt
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.simulation import MonteCarloSimulation
from supply_chain_sim.visualization import plot_safety_stock_distribution, plot_lead_time_impact

# Parameters
MEAN_DEMAND = 100  # units per day
DEMAND_STD = 20    # standard deviation
COVERAGE_DAYS = 7  # base safety stock coverage
SIMULATION_DAYS = 90  # simulate for 3 months
ITERATIONS = 1000  # number of Monte Carlo iterations
LEAD_TIMES = [1, 2, 3, 5, 7, 10]  # different lead times to analyze

# Create demand generator
demand_gen = DemandGenerator(
    mean=MEAN_DEMAND,
    std_dev=DEMAND_STD,
    seed=42  # for reproducibility
)

# Create simulation
simulation = MonteCarloSimulation(
    demand_generator=demand_gen,
    iterations=ITERATIONS
)

# Run simulation for different lead times
results = simulation.simulate_safety_stock(
    coverage_days=COVERAGE_DAYS,
    simulation_days=SIMULATION_DAYS,
    lead_times=LEAD_TIMES
)

# Analyze results
stats = simulation.analyze_results(results)
confidence_intervals = simulation.calculate_confidence_intervals(results)

# Print detailed analysis
print("\nSafety Stock Analysis by Lead Time")
print("-" * 50)
print(f"Base Coverage Duration: {COVERAGE_DAYS} days")
print(f"Mean Daily Demand: {MEAN_DEMAND} units")
print(f"Demand Std Dev: {DEMAND_STD} units")
print("\nResults:")
print("-" * 50)

for lt in LEAD_TIMES:
    lt_stats = stats[lt]
    ci_lower, ci_upper = confidence_intervals[lt]
    effective_coverage = COVERAGE_DAYS + lt
    
    print(f"\nLead Time: {lt} days")
    print(f"Effective Coverage: {effective_coverage} days")
    print(f"Mean Safety Stock: {lt_stats['mean']:.2f} units")
    print(f"Standard Deviation: {lt_stats['std']:.2f} units")
    print(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
    print(f"95th Percentile: {lt_stats['95th_percentile']:.2f} units")
    
    # Calculate key metrics
    service_level = (lt_stats['mean'] / (MEAN_DEMAND * effective_coverage)) * 100
    print(f"Service Level Coverage: {service_level:.1f}%")

# Create visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Safety Stock Distribution
plt.subplot(2, 1, 1)
plot_safety_stock_distribution(results)

# Plot 2: Lead Time Impact
plt.subplot(2, 1, 2)
plot_lead_time_impact(stats, metric='mean')

plt.tight_layout()
plt.show()

# Additional Analysis: Marginal Impact
print("\nMarginal Impact Analysis")
print("-" * 50)
print("How each additional day of lead time affects safety stock:")

prev_mean = None
for lt in LEAD_TIMES:
    current_mean = stats[lt]['mean']
    if prev_mean is not None:
        delta = current_mean - prev_mean
        delta_percent = (delta / prev_mean) * 100
        print(f"Lead Time {lt-1} → {lt}: +{delta:.2f} units ({delta_percent:.1f}% increase)")
    prev_mean = current_mean 