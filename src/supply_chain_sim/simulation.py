"""
Monte Carlo simulation module for supply chain analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from .demand import DemandGenerator

class MonteCarloSimulation:
    """Runs Monte Carlo simulations for supply chain analysis."""
    
    def __init__(
        self,
        demand_generator: DemandGenerator,
        iterations: int = 1000,
        seed: Optional[int] = None
    ):
        """
        Initialize the Monte Carlo simulation.

        Args:
            demand_generator (DemandGenerator): Generator for demand data
            iterations (int): Number of simulation iterations
            seed (Optional[int]): Random seed for reproducibility
        
        Raises:
            ValueError: If iterations is not positive
        """
        if iterations <= 0:
            raise ValueError("Number of iterations must be positive")
            
        self.demand_generator = demand_generator
        self.iterations = iterations
        if seed is not None:
            np.random.seed(seed)
    
    def simulate_safety_stock(
        self,
        coverage_days: float,
        simulation_days: int,
        lead_times: List[int]
    ) -> pd.DataFrame:
        """Run safety stock simulation for different lead times."""
        results = []
        
        for _ in range(self.iterations):
            demand = self.demand_generator.generate_daily_demand(simulation_days)
            
            for lead_time in lead_times:
                effective_coverage = coverage_days + lead_time
                safety_stock = self.demand_generator.calculate_safety_stock(
                    coverage_days=effective_coverage,
                    demand_history=demand
                )
                
                results.append({
                    'lead_time': lead_time,
                    'safety_stock': safety_stock,
                    'iteration': _
                })
        
        return pd.DataFrame(results)
    
    def analyze_results(
        self,
        simulation_results: pd.DataFrame
    ) -> Dict[int, Dict[str, float]]:
        """Analyze simulation results."""
        stats = {}
        
        for lead_time in simulation_results['lead_time'].unique():
            lt_data = simulation_results[
                simulation_results['lead_time'] == lead_time
            ]['safety_stock']
            
            stats[lead_time] = {
                'mean': lt_data.mean(),
                'std': lt_data.std(),
                'min': lt_data.min(),
                'max': lt_data.max(),
                'median': lt_data.median(),
                '95th_percentile': lt_data.quantile(0.95)
            }
        
        return stats
    
    def calculate_confidence_intervals(
        self,
        simulation_results: pd.DataFrame,
        confidence_level: float = 0.95
    ) -> Dict[int, Tuple[float, float]]:
        """Calculate confidence intervals for safety stock estimates."""
        intervals = {}
        
        for lead_time in simulation_results['lead_time'].unique():
            lt_data = simulation_results[
                simulation_results['lead_time'] == lead_time
            ]['safety_stock']
            
            mean = lt_data.mean()
            std_error = lt_data.std() / np.sqrt(len(lt_data))
            margin = std_error * 1.96  # For 95% confidence
            
            intervals[lead_time] = (mean - margin, mean + margin)
        
        return intervals 