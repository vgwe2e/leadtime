"""
Gradio web interface for supply chain simulation.
"""

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from .demand import DemandGenerator
from .simulation import MonteCarloSimulation

def format_currency(amount: float) -> str:
    """Format currency with appropriate suffixes."""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    return f"${amount:.0f}"

def analyze_lead_time_impact(
    mean_demand: float,
    demand_std: float,
    base_lead_time: int,
    coverage_days: int,
    unload_time: int,
    unit_cost: float,
    holding_cost_rate: float
) -> tuple:
    """Run lead time impact analysis and return results."""
    
    # Convert holding cost rate from percentage to decimal
    holding_cost_rate = holding_cost_rate / 100.0
    
    # Setup simulation
    demand_gen = DemandGenerator(mean=mean_demand, std_dev=demand_std, seed=42)
    simulation = MonteCarloSimulation(demand_gen, iterations=1000)
    
    # Define variation ranges
    small_var = [1, 2]
    medium_var = [3, 4]
    large_var = [9, 10]
    all_variations = small_var + medium_var + large_var
    
    # Calculate baseline
    baseline_results = simulation.simulate_safety_stock(
        coverage_days=coverage_days,
        simulation_days=90,
        lead_times=[base_lead_time + unload_time]
    )
    baseline_stats = simulation.analyze_results(baseline_results)
    baseline_stock = baseline_stats[base_lead_time + unload_time]['mean']
    baseline_cost = baseline_stock * unit_cost
    
    # Run simulation for all variations
    lead_times = [base_lead_time + var for var in all_variations]
    results = simulation.simulate_safety_stock(
        coverage_days=coverage_days,
        simulation_days=90,
        lead_times=[lt + unload_time for lt in lead_times]
    )
    stats = simulation.analyze_results(results)
    
    # Prepare results
    variations = []
    changes = []
    costs = []
    inventory_values = []
    
    for lt in lead_times:
        total_lt = lt + unload_time
        stock_level = stats[total_lt]['mean']
        change = stock_level - baseline_stock
        percent_change = (change / baseline_stock) * 100
        inventory_value = stock_level * unit_cost
        annual_holding_cost = inventory_value * holding_cost_rate
        
        variations.append(lt - base_lead_time)
        changes.append(percent_change)
        costs.append(annual_holding_cost)
        inventory_values.append(inventory_value)
    
    # Create visualization
    fig = plt.figure(figsize=(15, 10))
    
    # Plot 1: Safety Stock Changes
    plt.subplot(2, 1, 1)
    colors = ['green']*2 + ['yellow']*2 + ['red']*2
    bars = plt.bar(variations, changes, color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.2)
    plt.title('Impact on Safety Stock Levels', fontsize=12, pad=20)
    plt.xlabel('Additional Lead Time Days')
    plt.ylabel('% Increase in Safety Stock')
    
    # Add value labels on bars
    for bar, pct in zip(bars, changes):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%',
                ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Additional Cost Impact
    plt.subplot(2, 1, 2)
    additional_costs = [cost - baseline_cost * holding_cost_rate for cost in costs]
    bars = plt.bar(variations, additional_costs, color=colors)
    
    # Calculate significance threshold (25% increase from baseline)
    significance_threshold = baseline_cost * holding_cost_rate * 0.25  # 25% of baseline
    plt.axhline(y=significance_threshold, color='r', linestyle='--', 
                label='Significance Threshold (+25%)')
    
    plt.title('Additional Annual Holding Cost', fontsize=12, pad=20)
    plt.xlabel('Additional Lead Time Days')
    plt.ylabel('Additional Annual Cost ($)')
    
    # Add value labels on bars
    for bar, cost in zip(bars, additional_costs):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                format_currency(cost),
                ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    
    # Calculate max percentage increase in costs
    max_cost_increase = (max(costs) - baseline_cost * holding_cost_rate) / (baseline_cost * holding_cost_rate) * 100
    
    # Prepare text summary
    summary = f"""
### Baseline Analysis
- Base Lead Time: {base_lead_time} days (+{unload_time} day unload)
- Base Safety Stock: {baseline_stock:.0f} units
- Base Inventory Value: {format_currency(baseline_cost)}
- Base Annual Holding Cost: {format_currency(baseline_cost * holding_cost_rate)}

### Impact Analysis

**Small Variations (1-2 days)**
- +1 day: {changes[0]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + small_var[0] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[0])}
- +2 days: {changes[1]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + small_var[1] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[1])}

**Medium Variations (3-4 days)**
- +3 days: {changes[2]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + medium_var[0] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[2])}
- +4 days: {changes[3]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + medium_var[1] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[3])}

**Large Variations (9-10 days)**
- +9 days: {changes[4]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + large_var[0] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[4])}
- +10 days: {changes[5]:.1f}% increase
  * Additional Stock: {stats[base_lead_time + large_var[1] + unload_time]['mean'] - baseline_stock:.0f} units
  * Additional Annual Cost: {format_currency(additional_costs[5])}

### Key Findings
1. Small variations (1-2 days): {format_currency(np.mean(additional_costs[:2]))} avg. additional cost
   * {(np.mean(costs[:2]) - baseline_cost * holding_cost_rate) / (baseline_cost * holding_cost_rate) * 100:.1f}% increase from baseline
2. Medium variations (3-4 days): {format_currency(np.mean(additional_costs[2:4]))} avg. additional cost
   * {(np.mean(costs[2:4]) - baseline_cost * holding_cost_rate) / (baseline_cost * holding_cost_rate) * 100:.1f}% increase from baseline
3. Large variations (9-10 days): {format_currency(np.mean(additional_costs[4:]))} avg. additional cost
   * {(np.mean(costs[4:]) - baseline_cost * holding_cost_rate) / (baseline_cost * holding_cost_rate) * 100:.1f}% increase from baseline

### Impact Assessment
Maximum cost increase: {max_cost_increase:.1f}% above baseline holding costs
Baseline annual holding cost: {format_currency(baseline_cost * holding_cost_rate)}
Maximum additional annual cost: {format_currency(max(additional_costs))}

### Recommendation
{
    "LOW IMPACT: Quarterly review sufficient" 
    if max_cost_increase < 25
    else f"SIGNIFICANT IMPACT: Regular monitoring recommended - costs increase by {max_cost_increase:.1f}% (${format_currency(max(additional_costs))} additional annual cost)"
}

*Note: All costs are annual holding costs based on {holding_cost_rate*100:.0f}% of inventory value*
*Significance threshold is defined as a 25% increase (${format_currency(significance_threshold)}) from baseline holding costs*
"""
    
    return fig, summary

# Create Gradio interface
iface = gr.Interface(
    fn=analyze_lead_time_impact,
    inputs=[
        gr.Number(label="Mean Daily Demand", value=100),
        gr.Number(label="Demand Standard Deviation", value=20),
        gr.Number(label="Base Lead Time (days)", value=3),
        gr.Number(label="Safety Stock Coverage (days)", value=7),
        gr.Number(label="Unload Time (days)", value=1),
        gr.Number(label="Unit Cost ($)", value=50),
        gr.Number(label="Annual Holding Cost Rate (%)", value=20)
    ],
    outputs=[
        gr.Plot(label="Impact Analysis"),
        gr.Markdown(label="Analysis Summary")
    ],
    title="Supply Chain Lead Time Impact Analysis",
    description="""
    Analyze how changes in lead time affect safety stock requirements and costs.
    Input your supply chain parameters to see the impact of different lead time variations.
    
    - Green bars: Small variations (1-2 days)
    - Yellow bars: Medium variations (3-4 days)
    - Red bars: Large variations (9-10 days)
    """,
    theme="default"
) 