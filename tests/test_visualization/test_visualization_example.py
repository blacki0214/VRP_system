# test_visualization_example.py
from src.visualization.route_visualizater import RouteVisualizer
from src.models.route import Route
from src.models.location import Location
from src.models.parcel import Parcel

def test_visualization_manually():
    # Create sample routes
    route1 = Route(
        vehicle_id="DA1",
        locations=[
            Location(0, 0),  # Warehouse
            Location(1, 1),
            Location(2, 2),
            Location(0, 0)   # Return to warehouse
        ],
        parcels=[
            Parcel(1, Location(1, 1), 2.0),
            Parcel(2, Location(2, 2), 3.0)
        ]
    )

    route2 = Route(
        vehicle_id="DA2",
        locations=[
            Location(0, 0),
            Location(3, 3),
            Location(4, 4),
            Location(0, 0)
        ],
        parcels=[
            Parcel(3, Location(3, 3), 1.0),
            Parcel(4, Location(4, 4), 2.0)
        ]
    )

    # Initialize visualizer
    visualizer = RouteVisualizer()
    
    # Plot routes
    figure = visualizer.plot_routes([route1, route2])
    
    # Save plot
    figure.savefig('routes_visualization.png')

if __name__ == "__main__":
    test_visualization_manually()