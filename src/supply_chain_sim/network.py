"""
Network modeling module for supply chain simulation.
"""

import networkx as nx
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from .demand import DemandGenerator

@dataclass
class InventoryPolicy:
    """Represents inventory management policy for a node."""
    coverage_days: float
    reorder_point: float
    order_quantity: float
    
    def __post_init__(self):
        """Validate inventory policy parameters."""
        if self.coverage_days <= 0:
            raise ValueError("Coverage days must be positive")
        if self.reorder_point < 0:
            raise ValueError("Reorder point cannot be negative")
        if self.order_quantity <= 0:
            raise ValueError("Order quantity must be positive")

class SupplyChainNode:
    """Represents a node in the supply chain network."""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        demand_generator: Optional[DemandGenerator] = None,
        inventory_policy: Optional[InventoryPolicy] = None
    ):
        """
        Initialize a supply chain node.

        Args:
            node_id (str): Unique identifier for the node
            node_type (str): Type of node (e.g., 'supplier', 'dc', 'retailer')
            demand_generator (Optional[DemandGenerator]): Demand pattern for this node
            inventory_policy (Optional[InventoryPolicy]): Inventory management policy
        """
        self.node_id = node_id
        self.node_type = node_type
        self.demand_generator = demand_generator
        self.inventory_policy = inventory_policy
        self.inventory_level = 0.0
        self.pending_orders: List[Tuple[float, float]] = []  # (quantity, arrival_time)
        
    def place_order(self, quantity: float, arrival_time: float) -> None:
        """
        Place an order that will arrive at the specified time.

        Args:
            quantity (float): Order quantity
            arrival_time (float): Time when order will arrive
        """
        if quantity <= 0:
            raise ValueError("Order quantity must be positive")
        self.pending_orders.append((quantity, arrival_time))
        
    def receive_orders(self, current_time: float) -> float:
        """
        Process arriving orders at the current time.

        Args:
            current_time (float): Current simulation time

        Returns:
            float: Total quantity received
        """
        received = 0.0
        remaining_orders = []
        
        for quantity, arrival_time in self.pending_orders:
            if arrival_time <= current_time:
                received += quantity
                self.inventory_level += quantity
            else:
                remaining_orders.append((quantity, arrival_time))
                
        self.pending_orders = remaining_orders
        return received

class SupplyChainNetwork:
    """Manages the supply chain network structure and simulation."""
    
    def __init__(self):
        """Initialize an empty supply chain network."""
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, SupplyChainNode] = {}
        
    def add_node(
        self,
        node: SupplyChainNode
    ) -> None:
        """
        Add a node to the network.

        Args:
            node (SupplyChainNode): Node to add
        
        Raises:
            ValueError: If node ID already exists
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists")
            
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, node_type=node.node_type)
        
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        lead_time: float,
        capacity: Optional[float] = None
    ) -> None:
        """
        Add a directed edge between nodes.

        Args:
            source_id (str): ID of source node
            target_id (str): ID of target node
            lead_time (float): Transportation lead time
            capacity (Optional[float]): Maximum flow capacity
            
        Raises:
            ValueError: If nodes don't exist or lead time is invalid
        """
        if source_id not in self.nodes:
            raise ValueError(f"Source node {source_id} does not exist")
        if target_id not in self.nodes:
            raise ValueError(f"Target node {target_id} does not exist")
        if lead_time <= 0:
            raise ValueError("Lead time must be positive")
            
        self.graph.add_edge(
            source_id,
            target_id,
            lead_time=lead_time,
            capacity=capacity
        )
        
    def get_path_lead_time(
        self,
        source_id: str,
        target_id: str
    ) -> float:
        """
        Calculate total lead time along the shortest path.

        Args:
            source_id (str): Starting node ID
            target_id (str): Ending node ID

        Returns:
            float: Total lead time along shortest path
            
        Raises:
            nx.NetworkXNoPath: If no path exists
        """
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            total_lead_time = 0.0
            
            for i in range(len(path) - 1):
                total_lead_time += self.graph[path[i]][path[i + 1]]['lead_time']
                
            return total_lead_time
            
        except nx.NetworkXNoPath:
            raise nx.NetworkXNoPath(
                f"No path exists between {source_id} and {target_id}"
            )
            
    def simulate_disruption(
        self,
        node_id: str,
        duration: float,
        capacity_reduction: float
    ) -> None:
        """
        Simulate a disruption at a specific node.

        Args:
            node_id (str): ID of affected node
            duration (float): Duration of disruption
            capacity_reduction (float): Fraction of capacity reduced (0 to 1)
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
        if not 0 <= capacity_reduction <= 1:
            raise ValueError("Capacity reduction must be between 0 and 1")
            
        # Temporarily store original capacities
        edges = list(self.graph.in_edges(node_id)) + list(self.graph.out_edges(node_id))
        original_capacities = {}
        
        for edge in edges:
            if 'capacity' in self.graph[edge[0]][edge[1]]:
                original_capacities[edge] = self.graph[edge[0]][edge[1]]['capacity']
                self.graph[edge[0]][edge[1]]['capacity'] *= (1 - capacity_reduction)
                
        # Note: In a real simulation, we'd need to restore these capacities
        # after the disruption duration has passed 