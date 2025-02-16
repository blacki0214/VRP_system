import matplotlib.pyplot as plt
import numpy as np
from typing import List
from src.models.route import Route

class RouteVisualizer:
    def __init__(self, canvas_size=(800, 600)):
        self.canvas_size = canvas_size
        self.figure = None

    def plot_routes(self, routes: List[Route]):
        self.figure = plt.figure(figsize=(10, 8))
        
        # Plot warehouse
        plt.plot(0, 0, 'ks', markersize=10, label='Warehouse')
        
        # Plot routes with different colors
        colors = plt.cm.rainbow(np.linspace(0, 1, len(routes)))
        
        for route, color in zip(routes, colors):
            # Plot route lines
            x_coords = [loc.x for loc in route.locations]
            y_coords = [loc.y for loc in route.locations]
            plt.plot(x_coords, y_coords, '-', color=color, 
                    label=f'Vehicle {route.vehicle_id}')
            
            # Plot delivery points
            plt.plot(x_coords[1:-1], y_coords[1:-1], 'o', color=color)

        plt.legend()
        plt.grid(True)
        plt.title('Delivery Routes')
        return self.figure