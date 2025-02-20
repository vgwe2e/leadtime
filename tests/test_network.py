"""
Tests for the network modeling module.
"""

import pytest
import networkx as nx
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.network import (
    InventoryPolicy,
    SupplyChainNode,
    SupplyChainNetwork
)

@pytest.fixture
def inventory_policy():
    """Create a sample inventory policy for testing."""
    return InventoryPolicy(
        coverage_days=7,
        reorder_point=100,
        order_quantity=500
    )

@pytest.fixture
def demand_generator():
    """Create a sample demand generator for testing."""
    return DemandGenerator(mean=100, std_dev=20, seed=42)

@pytest.fixture
def supply_chain_node(demand_generator, inventory_policy):
    """Create a sample supply chain node for testing."""
    return SupplyChainNode(
        node_id="DC1",
        node_type="distribution_center",
        demand_generator=demand_generator,
        inventory_policy=inventory_policy
    )

@pytest.fixture
def network():
    """Create a sample supply chain network for testing."""
    return SupplyChainNetwork()

def test_inventory_policy_initialization():
    """Test InventoryPolicy initialization and validation."""
    # Valid initialization
    policy = InventoryPolicy(coverage_days=7, reorder_point=100, order_quantity=500)
    assert policy.coverage_days == 7
    assert policy.reorder_point == 100
    assert policy.order_quantity == 500
    
    # Test invalid parameters
    with pytest.raises(ValueError):
        InventoryPolicy(coverage_days=0, reorder_point=100, order_quantity=500)
    with pytest.raises(ValueError):
        InventoryPolicy(coverage_days=7, reorder_point=-1, order_quantity=500)
    with pytest.raises(ValueError):
        InventoryPolicy(coverage_days=7, reorder_point=100, order_quantity=0)

def test_supply_chain_node(supply_chain_node):
    """Test SupplyChainNode functionality."""
    # Test initialization
    assert supply_chain_node.node_id == "DC1"
    assert supply_chain_node.node_type == "distribution_center"
    assert supply_chain_node.inventory_level == 0.0
    assert len(supply_chain_node.pending_orders) == 0
    
    # Test order placement and receiving
    supply_chain_node.place_order(quantity=100, arrival_time=5.0)
    assert len(supply_chain_node.pending_orders) == 1
    
    # Test receiving orders
    received = supply_chain_node.receive_orders(current_time=3.0)
    assert received == 0.0  # Order shouldn't arrive yet
    assert len(supply_chain_node.pending_orders) == 1
    
    received = supply_chain_node.receive_orders(current_time=6.0)
    assert received == 100.0  # Order should arrive
    assert len(supply_chain_node.pending_orders) == 0
    assert supply_chain_node.inventory_level == 100.0
    
    # Test invalid order
    with pytest.raises(ValueError):
        supply_chain_node.place_order(quantity=0, arrival_time=1.0)

def test_supply_chain_network(network, supply_chain_node):
    """Test SupplyChainNetwork functionality."""
    # Add nodes
    network.add_node(supply_chain_node)
    network.add_node(SupplyChainNode("SUPPLIER1", "supplier"))
    
    assert len(network.nodes) == 2
    assert "DC1" in network.nodes
    assert "SUPPLIER1" in network.nodes
    
    # Test duplicate node
    with pytest.raises(ValueError):
        network.add_node(supply_chain_node)
    
    # Add edge
    network.add_edge("SUPPLIER1", "DC1", lead_time=3.0, capacity=1000.0)
    assert network.graph.has_edge("SUPPLIER1", "DC1")
    
    # Test invalid edge
    with pytest.raises(ValueError):
        network.add_edge("NONEXISTENT", "DC1", lead_time=3.0)
    with pytest.raises(ValueError):
        network.add_edge("SUPPLIER1", "DC1", lead_time=0)

def test_path_lead_time(network):
    """Test path lead time calculations."""
    # Create a simple network
    nodes = [
        SupplyChainNode("S1", "supplier"),
        SupplyChainNode("DC1", "distribution_center"),
        SupplyChainNode("R1", "retailer")
    ]
    
    for node in nodes:
        network.add_node(node)
    
    network.add_edge("S1", "DC1", lead_time=2.0)
    network.add_edge("DC1", "R1", lead_time=1.0)
    
    # Test lead time calculation
    assert network.get_path_lead_time("S1", "R1") == 3.0
    
    # Test non-existent path
    with pytest.raises(nx.NetworkXNoPath):
        network.get_path_lead_time("R1", "S1")  # Reverse direction

def test_simulate_disruption(network, supply_chain_node):
    """Test disruption simulation."""
    # Set up network
    network.add_node(supply_chain_node)
    network.add_node(SupplyChainNode("SUPPLIER1", "supplier"))
    network.add_edge("SUPPLIER1", "DC1", lead_time=3.0, capacity=1000.0)
    
    # Simulate disruption
    network.simulate_disruption("DC1", duration=5.0, capacity_reduction=0.5)
    
    # Check capacity reduction
    assert network.graph["SUPPLIER1"]["DC1"]["capacity"] == 500.0
    
    # Test invalid disruption parameters
    with pytest.raises(ValueError):
        network.simulate_disruption("NONEXISTENT", duration=5.0, capacity_reduction=0.5)
    with pytest.raises(ValueError):
        network.simulate_disruption("DC1", duration=5.0, capacity_reduction=1.5) 