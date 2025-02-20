"""
Demand generation module.
"""

import numpy as np
from typing import Optional

class DemandGenerator:
    def __init__(self, mean: float, std_dev: float, seed: Optional[int] = None):
        self.mean = mean
        self.std_dev = std_dev
        if seed is not None:
            np.random.seed(seed)
    
    def generate_daily_demand(self, days: int) -> np.ndarray:
        demand = np.random.normal(self.mean, self.std_dev, days)
        return np.maximum(demand, 0)  # Ensure non-negative
    
    def calculate_safety_stock(self, coverage_days: float, demand_history: Optional[np.ndarray] = None, days: Optional[int] = None) -> float:
        if demand_history is None:
            demand_history = self.generate_daily_demand(days or 30)
        return coverage_days * np.mean(demand_history) 