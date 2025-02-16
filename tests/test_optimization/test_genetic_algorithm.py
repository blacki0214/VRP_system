import unittest
from src.optimization.genetic_algorithm import GeneticAlgorithm
from src.models.route import Route
from src.models.parcel import Parcel
from src.models.location import Location

class TestGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        self.ga = GeneticAlgorithm()
        self.parcels = [
            Parcel(1, Location(1, 1), 2.0),
            Parcel(2, Location(2, 2), 3.0),
            Parcel(3, Location(3, 3), 1.0)
        ]
        self.constraints = {
            'vehicle_capacities': {'DA1': 10.0, 'DA2': 15.0},
            'max_distances': {'DA1': 100.0, 'DA2': 150.0}
        }

    def test_optimization(self):
        self.ga.parcels = self.parcels
        self.ga.constraints = self.constraints
        
        routes = self.ga.optimize()
        
        # Check if all parcels are assigned
        assigned_parcels = []
        for route in routes:
            assigned_parcels.extend(route.parcels)
        self.assertEqual(len(assigned_parcels), len(self.parcels))
        
        # Check constraints
        for route in routes:
            da_capacity = self.constraints['vehicle_capacities'][route.vehicle_id]
            total_weight = sum(p.weight for p in route.parcels)
            self.assertLessEqual(total_weight, da_capacity)