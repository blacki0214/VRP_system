# test_optimization_example.py
from src.optimization.genetic_algorithm import GeneticAlgorithm
from src.models.location import Location
from src.models.parcel import Parcel

def test_optimization_manually():
    # Create sample data
    parcels = [
        Parcel(1, Location(1, 1), 2.0),
        Parcel(2, Location(2, 2), 3.0),
        Parcel(3, Location(3, 3), 1.0)
    ]
    
    constraints = {
        'vehicle_capacities': {'DA1': 10.0, 'DA2': 15.0},
        'max_distances': {'DA1': 100.0, 'DA2': 150.0}
    }

    # Initialize optimizer
    ga = GeneticAlgorithm(
        population_size=50,
        generations=20,
        mutation_rate=0.1
    )
    
    ga.parcels = parcels
    ga.constraints = constraints

    # Run optimization
    routes = ga.optimize()
    
    # Print results
    for i, route in enumerate(routes):
        print(f"Route {i+1}:")
        print(f"Vehicle: {route.vehicle_id}")
        print(f"Distance: {route.total_distance}")
        print(f"Parcels: {len(route.parcels)}\n")

if __name__ == "__main__":
    test_optimization_manually()