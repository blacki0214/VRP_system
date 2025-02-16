from abc import ABC, abstractmethod
from typing import List, Dict
from src.models.route import Route
from src.models.parcel import Parcel

class BaseOptimizer(ABC):
    def __init__(self):
        self.routes: List[Route] = []
        self.parcels: List[Parcel] = []
        self.constraints: Dict = {}

    @abstractmethod
    def optimize(self) -> List[Route]:
        """Base optimization method"""
        pass

    def validate_solution(self, routes: List[Route]) -> bool:
        """Validate if solution meets all constraints"""
        for route in routes:
            if not self._check_capacity_constraint(route):
                return False
            if not self._check_distance_constraint(route):
                return False
        return True

    def _check_capacity_constraint(self, route: Route) -> bool:
        total_weight = sum(parcel.weight for parcel in route.parcels)
        return total_weight <= self.constraints['vehicle_capacities'][route.vehicle_id]

    def _check_distance_constraint(self, route: Route) -> bool:
        return route.total_distance <= self.constraints['max_distances'][route.vehicle_id]