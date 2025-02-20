"""
Tests for the Monte Carlo simulation framework.
"""

import pytest
import numpy as np
import pandas as pd
from supply_chain_sim.demand import DemandGenerator
from supply_chain_sim.simulation import MonteCarloSimulation

@pytest.fixture
def demand_generator():
    """Create a DemandGenerator instance for testing."""
    return DemandGenerator(mean=100, std_dev=20, seed=42)

@pytest.fixture
def simulation(demand_generator):
    """Create a MonteCarloSimulation instance for testing."""
    return MonteCarloSimulation(demand_generator, iterations=100, seed=42)

def test_simulation_initialization():
    """Test MonteCarloSimulation initialization."""
    generator = DemandGenerator(mean=100, std_dev=20)
    
    # Valid initialization
    sim = MonteCarloSimulation(generator, iterations=1000)
    assert sim.iterations == 1000
    assert sim.demand_generator == generator
    
    # Test invalid iterations
    with pytest.raises(ValueError):
        MonteCarloSimulation(generator, iterations=0)
    with pytest.raises(ValueError):
        MonteCarloSimulation(generator, iterations=-1)

def test_simulate_safety_stock(simulation):
    """Test safety stock simulation."""
    # Run simulation
    results = simulation.simulate_safety_stock(
        coverage_days=7,
        simulation_days=30,
        lead_times=[1, 2, 3]
    )
    
    # Check results structure
    assert isinstance(results, pd.DataFrame)
    assert set(results.columns) == {'lead_time', 'safety_stock', 'iteration'}
    assert len(results) == 300  # 100 iterations * 3 lead times
    
    # Check lead times
    assert set(results['lead_time'].unique()) == {1, 2, 3}
    
    # Check safety stock values are positive and increase with lead time
    assert (results['safety_stock'] > 0).all()
    
    # Calculate mean safety stock for each lead time
    mean_by_lt = results.groupby('lead_time')['safety_stock'].mean()
    assert mean_by_lt[2] > mean_by_lt[1]  # Longer lead time should need more safety stock
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        simulation.simulate_safety_stock(coverage_days=7, simulation_days=30, lead_times=[])
    with pytest.raises(ValueError):
        simulation.simulate_safety_stock(coverage_days=7, simulation_days=30, lead_times=[-1])

def test_analyze_results(simulation):
    """Test simulation results analysis."""
    # Generate test results
    results = simulation.simulate_safety_stock(
        coverage_days=7,
        simulation_days=30,
        lead_times=[1, 2]
    )
    
    # Analyze results
    stats = simulation.analyze_results(results)
    
    # Check structure
    assert set(stats.keys()) == {1, 2}
    for lt in [1, 2]:
        assert set(stats[lt].keys()) == {
            'mean', 'std', 'min', 'max', 'median', '95th_percentile'
        }
        
        # Check statistical properties
        assert stats[lt]['min'] <= stats[lt]['median'] <= stats[lt]['max']
        assert stats[lt]['mean'] > 0
        assert stats[lt]['std'] > 0

def test_calculate_confidence_intervals(simulation):
    """Test confidence interval calculations."""
    # Generate test results
    results = simulation.simulate_safety_stock(
        coverage_days=7,
        simulation_days=30,
        lead_times=[1, 2]
    )
    
    # Calculate confidence intervals
    intervals = simulation.calculate_confidence_intervals(results)
    
    # Check structure
    assert set(intervals.keys()) == {1, 2}
    
    for lt in [1, 2]:
        lower, upper = intervals[lt]
        assert lower < upper
        
        # Check that most values fall within the interval
        lt_data = results[results['lead_time'] == lt]['safety_stock']
        within_interval = (lt_data >= lower) & (lt_data <= upper)
        assert within_interval.mean() > 0.90  # At least 90% should be within interval 