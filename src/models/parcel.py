from dataclasses import dataclass
from .location import Location

@dataclass
class Parcel:
    id: int
    delivery_location: Location
    weight: float = 1.0