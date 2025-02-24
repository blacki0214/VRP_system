import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import os

class DataProcessor:
    def __init__(self):
        # Initialize data
        self.distance_data = None
        self.order_data = None
        self.distance_matrix = None
        self.cities = set()
        self.city_to_idx = {}
        self.idx_to_city = {}
        self.time_windows = {}
        self.service_time = 15  # 15 minutes service time per delivery
        
        # Track processed data
        self.cities = set()
        
        # Truck specifications
        self.truck_specifications = {
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
        """Load CSV files and perform initial validation"""
        try:
            # Load CSV files
            self.distance_data = pd.read_csv(distance_file)
            self.order_data = pd.read_csv(order_file)
            
            # Extract cities first
            self._extract_cities()
            
            print("\nData Loading Summary:")
            print(f"Number of distance records: {len(self.distance_data)}")
            print(f"Number of orders: {len(self.order_data)}")
            print(f"Number of unique cities: {len(self.cities)}")
            
            # Print first few cities for verification
            print("\nSample cities:", list(self.cities)[:5])
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _extract_cities(self) -> None:
        """Extract unique cities from both distance and order data"""
        try:
            # Get cities from distance data
            source_cities = set(self.distance_data['Source'].unique())
            dest_cities = set(self.distance_data['Destination'].unique())
            
            # Get cities from order data
            order_sources = set(self.order_data['Source'].unique())
            order_dests = set(self.order_data['Destination'].unique())
            
            # Combine all unique cities
            self.cities = source_cities.union(dest_cities).union(order_sources).union(order_dests)
            
            print(f"\nCity Extraction:")
            print(f"Cities from distance data (source): {len(source_cities)}")
            print(f"Cities from distance data (dest): {len(dest_cities)}")
            print(f"Cities from order data: {len(order_sources.union(order_dests))}")
            print(f"Total unique cities: {len(self.cities)}")
            
        except Exception as e:
            print(f"Error extracting cities: {e}")
            raise

    def create_distance_matrix(self) -> np.ndarray:
        """Create and return the distance matrix"""
        try:
            if not self.cities:
                raise ValueError("No cities found. Call load_data first.")

            # Sort cities for consistent indexing
            sorted_cities = sorted(list(self.cities))
            n_cities = len(sorted_cities)
            
            # Create city mappings
            self.city_to_idx = {city: idx for idx, city in enumerate(sorted_cities)}
            self.idx_to_city = {idx: city for idx, city in enumerate(sorted_cities)}
            
            # Initialize matrix with infinity (for cities with no direct connection)
            self.distance_matrix = np.full((n_cities, n_cities), np.inf)
            
            # Fill diagonal with zeros (distance to self)
            np.fill_diagonal(self.distance_matrix, 0)
            
            # Fill matrix with known distances
            for _, row in self.distance_data.iterrows():
                source = row['Source']
                dest = row['Destination']
                
                if source in self.city_to_idx and dest in self.city_to_idx:
                    i = self.city_to_idx[source]
                    j = self.city_to_idx[dest]
                    distance = row['Distance(M)']
                    
                    # Fill both directions
                    self.distance_matrix[i, j] = distance
                    self.distance_matrix[j, i] = distance
            
            print("\nDistance Matrix Creation:")
            print(f"Matrix shape: {self.distance_matrix.shape}")
            print(f"Number of finite distances: {np.sum(np.isfinite(self.distance_matrix))}")
            
            return self.distance_matrix
            
        except Exception as e:
            print(f"Error creating distance matrix:")
            print(f"Cities in data: {list(self.cities)[:5]}")
            print(f"Exception: {str(e)}")
            raise
    
    
    def get_distance(self, source: str, destination: str) -> float:
        """Get distance between two cities"""
        try:
            if source not in self.city_to_idx:
                raise ValueError(f"Source city {source} not found in city mapping")
            if destination not in self.city_to_idx:
                raise ValueError(f"Destination city {destination} not found in city mapping")
            
            i = self.city_to_idx[source]
            j = self.city_to_idx[destination]
            distance = self.distance_matrix[i, j]
            
            if np.isinf(distance):
                print(f"Warning: No direct connection between {source} and {destination}")
                return float('inf')
                
            return distance
            
        except Exception as e:
            print(f"Error getting distance: {e}")
            raise

    def calculate_route_distance(self, route: List[str]) -> float:
        """Calculate total distance for a route"""
        try:
            if len(route) < 2:
                return 0.0
            
            total_distance = 0
            for i in range(len(route) - 1):
                distance = self.get_distance(route[i], route[i + 1])
                if np.isinf(distance):
                    return float('inf')
                total_distance += distance
                
            return total_distance
            
        except Exception as e:
            print(f"Error calculating route distance: {e}")
            raise

    def get_distance_stats(self) -> Dict:
        """Get statistics about distances"""
        try:
            finite_distances = self.distance_matrix[np.isfinite(self.distance_matrix)]
            
            return {
                'min_distance': np.min(finite_distances),
                'max_distance': np.max(finite_distances),
                'avg_distance': np.mean(finite_distances),
                'total_connections': len(finite_distances)
            }
        except Exception as e:
            print(f"Error calculating distance stats: {e}")
            raise
        
    def process_time_windows(self):
        """Process and validate time windows from order data"""
        try:
            print("\nProcessing time windows...")
            
            # Convert time columns to datetime
            self.order_data['Available_Time'] = pd.to_datetime(self.order_data['Available_Time'])
            self.order_data['Deadline'] = pd.to_datetime(self.order_data['Deadline'])
            
            # Create time windows dictionary
            for _, row in self.order_data.iterrows():
                self.time_windows[row['Order_ID']] = {
                    'order_id': row['Order_ID'],
                    'available_time': row['Available_Time'],
                    'deadline': row['Deadline'],
                    'source': row['Source'],
                    'destination': row['Destination'],
                    'weight': row['Weight'],
                    'service_time': self.service_time
                }
            
            self._validate_time_windows()
            self._print_time_window_summary()
            
        except Exception as e:
            print(f"Error processing time windows: {e}")
            raise
        
    def _validate_time_windows(self):
        """Validate time window constraints"""
        invalid_windows = []
        
        for order_id, window in self.time_windows.items():
            # Check if deadline is after available time
            if window['deadline'] <= window['available_time']:
                invalid_windows.append((order_id, "Deadline before available time"))
            
            # Check if window duration is reasonable (e.g., > service time)
            duration = (window['deadline'] - window['available_time']).total_seconds() / 60
            if duration < self.service_time:
                invalid_windows.append((order_id, "Time window shorter than service time"))
        
        if invalid_windows:
            print("\nWarning: Invalid time windows found:")
            for order_id, reason in invalid_windows:
                print(f"Order {order_id}: {reason}")
                
    def check_time_feasibility(self, route: List[str], start_time: datetime, truck_type: str) -> Tuple[bool, str]:
        """Check if route is feasible within time windows"""
        try:
            current_time = start_time
            vehicle_speed = self.truck_specifications[truck_type]['speed']
            
            for i in range(len(route) - 1):
                # Calculate travel time to next location
                distance = self.get_distance(route[i], route[i + 1])
                travel_time = (distance / vehicle_speed) * 60  # Convert to minutes
                
                # Update current time with travel
                current_time += timedelta(minutes=travel_time)
                
                # Find order for this destination
                order_id = self._find_order_for_locations(route[i], route[i + 1])
                if order_id:
                    window = self.time_windows[order_id]
                    
                    # Check if arrival is too early
                    if current_time < window['available_time']:
                        current_time = window['available_time']
                    
                    # Check if arrival is too late
                    if current_time > window['deadline']:
                        return False, f"Late arrival for order {order_id}"
                    
                    # Add service time
                    current_time += timedelta(minutes=self.service_time)
            
            return True, "Route is time-feasible"
            
        except Exception as e:
            return False, str(e)
        
    def _find_order_for_locations(self, source: str, destination: str) -> str:
        """Find order ID for given source and destination pair"""
        for order_id, window in self.time_windows.items():
            if window['source'] == source and window['destination'] == destination:
                return order_id
        return None
    
    def calculate_arrival_times(self, route: List[str], start_time: datetime, truck_type: str) -> List[datetime]:
        """Calculate arrival times for each stop in the route"""
        arrival_times = [start_time]
        current_time = start_time
        vehicle_speed = self.truck_specifications[truck_type]['speed']
        
        for i in range(len(route) - 1):
            # Calculate travel time
            distance = self.get_distance(route[i], route[i + 1])
            travel_time = (distance / vehicle_speed) * 60
            
            # Update current time
            current_time += timedelta(minutes=travel_time)
            
            # Add service time if it's a delivery point
            if self._find_order_for_locations(route[i], route[i + 1]):
                current_time += timedelta(minutes=self.service_time)
            
            arrival_times.append(current_time)
        
        return arrival_times
    
    def _print_time_window_summary(self):
        """Print summary of time window data"""
        print("\nTime Window Summary:")
        print(f"Total orders: {len(self.time_windows)}")
        
        # Calculate some statistics
        durations = [(window['deadline'] - window['available_time']).total_seconds() / 3600 
                    for window in self.time_windows.values()]
        
        print(f"Average time window duration: {np.mean(durations):.2f} hours")
        print(f"Min time window duration: {np.min(durations):.2f} hours")
        print(f"Max time window duration: {np.max(durations):.2f} hours")

def main():
    """Test time window processing"""
    try:
        # Initialize processor
        processor = DataProcessor()
        
        # Load and process data
        processor.load_data('distance.csv', 'order_large.csv')
        processor.create_distance_matrix()
        processor.process_time_windows()
        
        # Test time feasibility for a sample route
        print("\nTesting time feasibility:")
        # Get first order for testing
        first_order = next(iter(processor.time_windows.values()))
        sample_route = [first_order['source'], first_order['destination']]
        start_time = first_order['available_time']
        
        is_feasible, reason = processor.check_time_feasibility(
            sample_route,
            start_time,
            '9.6'  # Using smallest truck type
        )
        
        print(f"Route feasible: {is_feasible}")
        print(f"Reason: {reason}")
        
        # Show arrival times
        arrival_times = processor.calculate_arrival_times(
            sample_route,
            start_time,
            '9.6'
        )
        
        print("\nArrival Times:")
        for location, time in zip(sample_route, arrival_times):
            print(f"{location}: {time}")
        
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()