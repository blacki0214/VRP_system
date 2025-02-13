from dataclasses import dataclass
from .location import Location


@dataclass
class Parcel:
    id: int
    delivery_location: Location
    weight: float = 1.0

    def validate(self) -> bool:
        """Kiểm tra tính hợp lệ của gói hàng"""
        return self.weight > 0
