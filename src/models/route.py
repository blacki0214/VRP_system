from dataclasses import dataclass
from typing import List, Dict
from .location import Location
from .parcel import Parcel
from datetime import datetime


@dataclass
class Route:
    vehicle_id: str
    truck_type: str
    order_sequence: List[str]  # Order IDs in sequence
    cities_sequence: List[str]  # Cities in sequence
    start_time: datetime
    
    total_distance: float = 0.0
    total_cost: float = 0.0
    is_feasible: bool = True
    violation_reason: str = ""

    def calculate_total_distance(self) -> float:
        """Calculate the total distance of the route"""
        total = 0.0
        for i in range(len(self.locations) - 1):
            total += self.locations[i].distance_to(self.locations[i + 1])
        self.total_distance = total
        return total

    def get_total_weight(self) -> float:
        """Caculate the total weight of the route"""
        return sum(parcel.weight for parcel in self.parcels)
