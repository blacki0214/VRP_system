from dataclasses import dataclass
from .location import Location


@dataclass
class Parcel:
    id: int
    delivery_location: Location
    weight: float = 1.0

    def validate(self) -> bool:
        """Check the validity of the package"""
        return self.weight > 0
