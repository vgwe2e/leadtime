"""
Visualization module for supply chain network analysis.
"""

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Dict, Optional, Any
from .network import SupplyChainNetwork

def plot_network(
    network: SupplyChainNetwork,
    figsize: tuple = (12, 8),
    node_size: int = 2000,
    node_color: str = 'lightblue',
    title: str = 'Supply Chain Network'
) -> None:
    """
    Plot the supply chain network structure.

    Args:
        network (SupplyChainNetwork): Network to visualize
        figsize (tuple): Figure size (width, height)
        node_size (int): Size of nodes in visualization
        node_color (str): Color of nodes
        title (str): Plot title
    """
    plt.figure(figsize=figsize)
    
    # Create position layout
    pos = nx.spring_layout(network.graph)
    
    # Draw nodes
    nx.draw_networkx_nodes(
        network.graph,
        pos,
        node_color=node_color,
        node_size=node_size
    )
    
    # Draw edges with lead time labels
    nx.draw_networkx_edges(network.graph, pos, edge_color='gray', arrows=True)
    edge_labels = nx.get_edge_attributes(network.graph, 'lead_time')
    nx.draw_networkx_edge_labels(
        network.graph,
        pos,
        edge_labels={k: f'LT={v}d' for k, v in edge_labels.items()}
    )
    
    # Add node labels with type
    labels = {
        node: f'{node}\n({data["node_type"]})'
        for node, data in network.graph.nodes(data=True)
    }
    nx.draw_networkx_labels(network.graph, pos, labels)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()

def plot_safety_stock_distribution(
    simulation_results: pd.DataFrame,
    title: str = 'Safety Stock Distribution by Lead Time'
) -> None:
    """
    Plot safety stock distribution for different lead times.

    Args:
        simulation_results (pd.DataFrame): Results from Monte Carlo simulation
        title (str): Plot title
    """
    plt.figure(figsize=(12, 6))
    
    sns.boxplot(
        data=simulation_results,
        x='lead_time',
        y='safety_stock'
    )
    
    plt.title(title)
    plt.xlabel('Lead Time (days)')
    plt.ylabel('Safety Stock Level')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

def plot_inventory_flow(
    node_data: Dict[str, Dict[str, Any]],
    title: str = 'Inventory Flow Over Time'
) -> None:
    """
    Plot inventory levels and order patterns over time.

    Args:
        node_data (Dict[str, Dict[str, Any]]): Time series data for each node
        title (str): Plot title
    """
    plt.figure(figsize=(12, 6))
    
    for node_id, data in node_data.items():
        plt.plot(
            data['time'],
            data['inventory_level'],
            label=f'{node_id} Inventory',
            marker='o'
        )
        
        # Plot orders as vertical lines
        for order_time, order_qty in zip(
            data.get('order_times', []),
            data.get('order_quantities', [])
        ):
            plt.vlines(
                order_time,
                0,
                order_qty,
                colors='gray',
                linestyles='dashed',
                alpha=0.3
            )
    
    plt.title(title)
    plt.xlabel('Time (days)')
    plt.ylabel('Inventory Level')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

def plot_lead_time_impact(
    stats: Dict[int, Dict[str, float]],
    metric: str = 'mean',
    title: Optional[str] = None
) -> None:
    """
    Plot the impact of lead time on safety stock metrics.

    Args:
        stats (Dict[int, Dict[str, float]]): Statistics from simulation analysis
        metric (str): Metric to plot ('mean', 'std', etc.)
        title (str, optional): Plot title
    """
    lead_times = sorted(stats.keys())
    values = [stats[lt][metric] for lt in lead_times]
    
    plt.figure(figsize=(10, 6))
    plt.plot(lead_times, values, marker='o')
    
    if title is None:
        title = f'Impact of Lead Time on Safety Stock ({metric})'
    
    plt.title(title)
    plt.xlabel('Lead Time (days)')
    plt.ylabel(f'Safety Stock {metric.capitalize()}')
    plt.grid(True, alpha=0.3)
    plt.tight_layout() 