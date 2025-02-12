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