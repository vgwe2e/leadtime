# Supply Chain Network Simulation

A Python package for simulating and analyzing safety stock levels across supply chain networks using Monte Carlo simulation.

## Features

- **Monte Carlo Simulation**: Analyze safety stock requirements under varying lead times
- **Network Modeling**: Model complex supply chain networks with multiple nodes and relationships
- **Demand Generation**: Generate realistic demand patterns using configurable distributions
- **Inventory Management**: Track inventory levels and implement ordering policies
- **Disruption Analysis**: Simulate and analyze the impact of network disruptions
- **Visualization**: Comprehensive visualization tools for network structure and simulation results

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/supply-chain-sim.git
cd supply-chain-sim

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.network import SupplyChainNode, SupplyChainNetwork
from supply_chain_sim.simulation import MonteCarloSimulation
from supply_chain_sim.visualization import plot_network, plot_safety_stock_distribution

# Create a simple supply chain network
network = SupplyChainNetwork()

# Add nodes
supplier = SupplyChainNode("S1", "supplier")
dc = SupplyChainNode(
    "DC1",
    "distribution_center",
    demand_generator=DemandGenerator(mean=100, std_dev=20)
)
retailer = SupplyChainNode("R1", "retailer")

for node in [supplier, dc, retailer]:
    network.add_node(node)

# Add connections
network.add_edge("S1", "DC1", lead_time=3.0)
network.add_edge("DC1", "R1", lead_time=1.0)

# Visualize the network
plot_network(network)

# Run simulation
simulation = MonteCarloSimulation(dc.demand_generator)
results = simulation.simulate_safety_stock(
    coverage_days=7,
    simulation_days=30,
    lead_times=[1, 2, 3, 4]
)

# Analyze results
stats = simulation.analyze_results(results)
plot_safety_stock_distribution(results)
```

## Documentation

### Core Components

#### DemandGenerator

Generates daily demand patterns using configurable distributions:

```python
generator = DemandGenerator(
    mean=100,      # Mean daily demand
    std_dev=20,    # Standard deviation
    seed=42        # Optional seed for reproducibility
)

# Generate 30 days of demand
demand = generator.generate_daily_demand(days=30)
```

#### SupplyChainNetwork

Models the supply chain network structure:

```python
network = SupplyChainNetwork()

# Add nodes and edges
network.add_node(SupplyChainNode("DC1", "distribution_center"))
network.add_node(SupplyChainNode("R1", "retailer"))
network.add_edge("DC1", "R1", lead_time=2.0, capacity=1000.0)

# Calculate path metrics
total_lead_time = network.get_path_lead_time("DC1", "R1")
```

#### MonteCarloSimulation

Runs simulations to analyze safety stock requirements:

```python
simulation = MonteCarloSimulation(
    demand_generator=generator,
    iterations=1000
)

# Run simulation
results = simulation.simulate_safety_stock(
    coverage_days=7,
    simulation_days=30,
    lead_times=[1, 2, 3]
)

# Analyze results
stats = simulation.analyze_results(results)
intervals = simulation.calculate_confidence_intervals(results)
```

### Visualization

The package provides several visualization functions:

- `plot_network()`: Visualize network structure
- `plot_safety_stock_distribution()`: Show safety stock distributions
- `plot_inventory_flow()`: Display inventory levels over time
- `plot_lead_time_impact()`: Analyze lead time impact on metrics

## Testing

Run the test suite:

```bash
pytest tests/
```

For coverage report:

```bash
pytest --cov=supply_chain_sim tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NetworkX for graph modeling
- Matplotlib and Seaborn for visualization
- Pandas for data analysis
- NumPy for numerical computations 