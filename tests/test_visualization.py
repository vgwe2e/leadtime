"""
Tests for the visualization module.
"""

import pytest
import pandas as pd
import matplotlib.pyplot as plt
from supply_chain_sim.network import SupplyChainNode, SupplyChainNetwork
from supply_chain_sim.visualization import (
    plot_network,
    plot_safety_stock_distribution,
    plot_inventory_flow,
    plot_lead_time_impact
)

@pytest.fixture
def sample_network():
    """Create a sample network for testing visualizations."""
    network = SupplyChainNetwork()
    
    # Add nodes
    nodes = [
        SupplyChainNode("S1", "supplier"),
        SupplyChainNode("DC1", "distribution_center"),
        SupplyChainNode("R1", "retailer")
    ]
    
    for node in nodes:
        network.add_node(node)
    
    # Add edges
    network.add_edge("S1", "DC1", lead_time=2.0)
    network.add_edge("DC1", "R1", lead_time=1.0)
    
    return network

@pytest.fixture
def sample_simulation_results():
    """Create sample simulation results for testing."""
    return pd.DataFrame({
        'lead_time': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'safety_stock': [100, 110, 90, 150, 160, 140, 200, 210, 190],
        'iteration': [0, 1, 2, 0, 1, 2, 0, 1, 2]
    })

@pytest.fixture
def sample_node_data():
    """Create sample node time series data for testing."""
    return {
        'DC1': {
            'time': [0, 1, 2, 3],
            'inventory_level': [100, 80, 120, 90],
            'order_times': [1, 2],
            'order_quantities': [50, 60]
        },
        'R1': {
            'time': [0, 1, 2, 3],
            'inventory_level': [50, 40, 30, 60],
            'order_times': [1],
            'order_quantities': [40]
        }
    }

@pytest.fixture
def sample_stats():
    """Create sample statistics for testing."""
    return {
        1: {'mean': 100, 'std': 10},
        2: {'mean': 150, 'std': 15},
        3: {'mean': 200, 'std': 20}
    }

def test_plot_network(sample_network):
    """Test network visualization."""
    plt.clf()  # Clear any existing plots
    plot_network(sample_network)
    
    # Check that the plot was created
    assert plt.gcf() is not None
    plt.close()

def test_plot_safety_stock_distribution(sample_simulation_results):
    """Test safety stock distribution visualization."""
    plt.clf()
    plot_safety_stock_distribution(sample_simulation_results)
    
    # Check that the plot was created
    assert plt.gcf() is not None
    plt.close()

def test_plot_inventory_flow(sample_node_data):
    """Test inventory flow visualization."""
    plt.clf()
    plot_inventory_flow(sample_node_data)
    
    # Check that the plot was created
    assert plt.gcf() is not None
    plt.close()

def test_plot_lead_time_impact(sample_stats):
    """Test lead time impact visualization."""
    plt.clf()
    plot_lead_time_impact(sample_stats)
    
    # Check that the plot was created
    assert plt.gcf() is not None
    plt.close()

def test_plot_lead_time_impact_custom_metric(sample_stats):
    """Test lead time impact visualization with custom metric."""
    plt.clf()
    plot_lead_time_impact(sample_stats, metric='std')
    
    # Check that the plot was created
    assert plt.gcf() is not None
    plt.close() 