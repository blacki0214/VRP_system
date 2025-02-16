from typing import List, Dict
from src.models.route import Route

class PerformanceDashboard:
    def __init__(self):
        self.metrics = {}

    def calculate_metrics(self, routes: List[Route]) -> Dict:
        self.metrics = {
            'total_distance': sum(r.total_distance for r in routes),
            'total_deliveries': sum(len(r.parcels) for r in routes),
            'vehicle_utilization': self._calculate_utilization(routes),
            'route_statistics': self._calculate_route_stats(routes)
        }
        return self.metrics

    def _calculate_utilization(self, routes: List[Route]) -> Dict:
        utilization = {}
        for route in routes:
            total_weight = sum(p.weight for p in route.parcels)
            capacity = route.vehicle_capacity
            utilization[route.vehicle_id] = (total_weight / capacity) * 100
        return utilization

    def _calculate_route_stats(self, routes: List[Route]) -> Dict:
        return {
            'min_distance': min(r.total_distance for r in routes),
            'max_distance': max(r.total_distance for r in routes),
            'avg_distance': sum(r.total_distance for r in routes) / len(routes)
        }