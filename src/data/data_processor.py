import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os


class DataProcessor:
    def __init__(self):
        # Data storage
        self.distance_data: Optional[pd.DataFrame] = None
        self.order_data: Optional[pd.DataFrame] = None
        self.distance_matrix: Optional[np.ndarray] = None

        # Mappings and lookups
        self.cities: set = set()
        self.city_to_idx: Dict[str, int] = {}
        self.truck_specifications: Dict[str, Dict] = {
            '16.5': {
                'length': 16.5,
                'inner_size': (16.1, 2.5),
                'weight_capacity': 10000,
                'cost_per_km': 3,
                'speed': 40
            },
            '12.5': {
                'length': 12.5,
                'inner_size': (12.1, 2.5),
                'weight_capacity': 5000,
                'cost_per_km': 2,
                'speed': 40
            },
            '9.6': {
                'length': 9.6,
                'inner_size': (9.1, 2.3),
                'weight_capacity': 2000,
                'cost_per_km': 1,
                'speed': 40
            }
        }

    def load_data(self, distance_file: str, order_file: str) -> None:
        """Load and validate input data"""
        try:
            # Load CSV files
            self.distance_data = pd.read_csv(distance_file)
            self.order_data = pd.read_csv(order_file)

            # Process time columns
            self._process_time_windows()

            # Extract unique cities
            self._extract_cities()

            # Create distance matrix
            self._create_distance_matrix()

            print(f"\nData loaded successfully:")
            self._print_data_summary()

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _process_time_windows(self) -> None:
        """Process time window columns"""
        time_columns = ['Available_Time', 'Deadline']
        for col in time_columns:
            self.order_data[col] = pd.to_datetime(self.order_data[col])

    def _extract_cities(self) -> None:
        """Extract unique cities from data"""
        source_cities = set(self.distance_data['Source'].unique())
        dest_cities = set(self.distance_data['Destination'].unique())
        self.cities = source_cities.union(dest_cities)
        self.city_to_idx = {city: idx for idx, city in enumerate(sorted(self.cities))}

    def _create_distance_matrix(self) -> None:
        """Create distance matrix from distance data"""
        n_cities = len(self.cities)
        self.distance_matrix = np.zeros((n_cities, n_cities))

        for _, row in self.distance_data.iterrows():
            i = self.city_to_idx[row['Source']]
            j = self.city_to_idx[row['Destination']]
            self.distance_matrix[i, j] = row['Distance(M)']

    def get_distance(self, source: str, destination: str) -> float:
        """Get distance between two cities"""
        if source not in self.city_to_idx or destination not in self.city_to_idx:
            raise ValueError(f"Invalid city names: {source} or {destination}")

        i = self.city_to_idx[source]
        j = self.city_to_idx[destination]
        return self.distance_matrix[i, j]

    def get_truck_capacity(self, truck_type: str) -> float:
        """Get weight capacity for truck type"""
        if truck_type not in self.truck_specifications:
            raise ValueError(f"Invalid truck type: {truck_type}")
        return self.truck_specifications[truck_type]['weight_capacity']

    def get_route_cost(self, distance: float, truck_type: str) -> float:
        """Calculate route cost for given distance and truck type"""
        if truck_type not in self.truck_specifications:
            raise ValueError(f"Invalid truck type: {truck_type}")
        return distance * self.truck_specifications[truck_type]['cost_per_km']

    def get_time_window(self, order_id: str) -> Tuple[datetime, datetime]:
        """Get time window for an order"""
        order = self.order_data[self.order_data['Order_ID'] == order_id]
        if order.empty:
            raise ValueError(f"Invalid order ID: {order_id}")

        return (order['Available_Time'].iloc[0], order['Deadline'].iloc[0])

    def is_feasible_route(self, route: List[str], truck_type: str) -> Tuple[bool, str]:
        """
        Check if route is feasible for given truck type
        Returns: (is_feasible, reason)
        """
        if len(route) < 2:
            return False, "Route must have at least 2 points"

        # Check distance constraint
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.get_distance(route[i], route[i + 1])

        # Check truck constraints
        truck_spec = self.truck_specifications.get(truck_type)
        if not truck_spec:
            return False, f"Invalid truck type: {truck_type}"

        return True, "Route is feasible"

    def _print_data_summary(self) -> None:
        """Print summary of loaded data"""
        print("\nData Summary:")
        print(f"Number of distance records: {len(self.distance_data)}")
        print(f"Number of orders: {len(self.order_data)}")
        print(f"Number of unique cities: {len(self.cities)}")
        print(f"Distance matrix shape: {self.distance_matrix.shape}")


def main():
    """Example usage of DataProcessor"""
    try:
        # Initialize processor
        processor = DataProcessor()

        # Load data
        processor.load_data('distance.csv', 'order_large.csv')

        # Example operations
        print("\nExample Operations:")

        # Get distance between two cities
        source = processor.cities.pop()
        dest = processor.cities.pop()
        distance = processor.get_distance(source, dest)
        print(f"Distance from {source} to {dest}: {distance}km")

        # Calculate route cost
        cost = processor.get_route_cost(distance, '9.6')
        print(f"Cost for {distance}km with 9.6m truck: ${cost}")

        # Check route feasibility
        route = [source, dest]
        is_feasible, reason = processor.is_feasible_route(route, '9.6')
        print(f"Route feasible: {is_feasible} ({reason})")

    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    main()