"""
Tests for the demand generation module.
"""

import pytest
import numpy as np
from supply_chain_sim.demand import DemandGenerator

def test_demand_generator_initialization():
    """Test DemandGenerator initialization with valid and invalid parameters."""
    # Valid initialization
    generator = DemandGenerator(mean=100, std_dev=20)
    assert generator.mean == 100
    assert generator.std_dev == 20
    
    # Test negative mean
    with pytest.raises(ValueError):
        DemandGenerator(mean=-100, std_dev=20)
    
    # Test negative std_dev
    with pytest.raises(ValueError):
        DemandGenerator(mean=100, std_dev=-20)

def test_generate_daily_demand():
    """Test daily demand generation."""
    generator = DemandGenerator(mean=100, std_dev=20, seed=42)
    days = 30
    
    # Generate demand
    demand = generator.generate_daily_demand(days)
    
    # Check shape and non-negativity
    assert len(demand) == days
    assert np.all(demand >= 0)
    
    # Check statistical properties (rough approximation due to randomness)
    assert 80 <= np.mean(demand) <= 120
    
    # Test invalid days
    with pytest.raises(ValueError):
        generator.generate_daily_demand(0)
    with pytest.raises(ValueError):
        generator.generate_daily_demand(-1)

def test_calculate_safety_stock():
    """Test safety stock calculation."""
    generator = DemandGenerator(mean=100, std_dev=20, seed=42)
    
    # Test with generated demand
    safety_stock = generator.calculate_safety_stock(coverage_days=7, days=30)
    assert safety_stock > 0
    
    # Test with provided demand history
    demand_history = np.array([100, 110, 90, 95, 105])
    safety_stock = generator.calculate_safety_stock(
        coverage_days=7,
        demand_history=demand_history
    )
    assert safety_stock == 7 * np.mean(demand_history)
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        generator.calculate_safety_stock(coverage_days=-1, days=30)
    with pytest.raises(ValueError):
        generator.calculate_safety_stock(coverage_days=7) 