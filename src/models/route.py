from dataclasses import dataclass
from typing import List
from .location import Location
from .parcel import Parcel


@dataclass
class Route:
    vehicle_id: str
    locations: List[Location]
    parcels: List[Parcel]
    total_distance: float = 0.0

    def calculate_total_distance(self) -> float:
        """Tính tổng khoảng cách của tuyến đường"""
        total = 0.0
        for i in range(len(self.locations) - 1):
            total += self.locations[i].distance_to(self.locations[i + 1])
        self.total_distance = total
        return total

    def get_total_weight(self) -> float:
        """Tính tổng trọng lượng các gói hàng"""
        return sum(parcel.weight for parcel in self.parcels)
