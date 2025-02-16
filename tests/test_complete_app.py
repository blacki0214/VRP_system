# test_complete_system.py
from src.agents.master_routing_agent import MasterRoutingAgent
from src.models.location import Location
from src.models.parcel import Parcel

def test_complete_system():
    # Initialize MRA
    mra = MasterRoutingAgent("MRA_1")
    
    # Add delivery agents
    mra.delivery_agents = {
        "DA1": {"capacity": 10.0, "max_distance": 100.0},
        "DA2": {"capacity": 15.0, "max_distance": 150.0}
    }
    
    # Add parcels
    mra.parcels = [
        Parcel(1, Location(1, 1), 2.0),
        Parcel(2, Location(2, 2), 3.0),
        Parcel(3, Location(3, 3), 1.0),
        Parcel(4, Location(4, 4), 2.0)
    ]
    
    # Run optimization and visualization
    routes = mra.optimize_routes()
    
    # Print results
    print("\nOptimization Results:")
    for route in routes:
        print(f"\nVehicle {route.vehicle_id}:")
        print(f"Total Distance: {route.total_distance:.2f}")
        print(f"Number of Parcels: {len(route.parcels)}")
        print("Delivery Locations:", 
              [(loc.x, loc.y) for loc in route.locations[1:-1]])

if __name__ == "__main__":
    test_complete_system()