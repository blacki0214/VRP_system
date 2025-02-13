from dataclasses import dataclass


@dataclass
class Location:
    x: float
    y: float

    def distance_to(self, other: 'Location') -> float:
        """Tính khoảng cách đến một điểm khác"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
