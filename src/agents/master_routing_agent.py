from src.optimization.genetic_algorithm import GeneticAlgorithm
from src.visualization.route_visualizater import RouteVisualizer

class MasterRoutingAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.optimizer = GeneticAlgorithm()
        self.visualizer = RouteVisualizer()
        self.delivery_agents = {}
        self.parcels = []

    def optimize_routes(self):
        # Set up optimizer
        self.optimizer.parcels = self.parcels
        self.optimizer.constraints = {
            'vehicle_capacities': {da_id: info['capacity'] 
                                 for da_id, info in self.delivery_agents.items()},
            'max_distances': {da_id: info['max_distance']
                            for da_id, info in self.delivery_agents.items()}
        }

        # Run optimization
        optimized_routes = self.optimizer.optimize()

        # Visualize routes
        if optimized_routes:
            self.visualizer.plot_routes(optimized_routes)

        return optimized_routes