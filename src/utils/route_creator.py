from typing import List, Optional
from src.models.route import Route
from src.models.location import Location
from src.models.parcel import Parcel
from src.utils.distance_calculator import calculate_distance

class RouteCreator:
    def __init__(self, depot_location: Location):
        self.depot_location = depot_location

    def create_route(
        self,
        vehicle_id: str,
        parcels: List[Parcel],
        vehicle_capacity: float,
        max_distance: float
    ) -> Optional[Route]:
        """
        Create a route for a vehicle considering capacity and distance constraints.
        
        Args:
            vehicle_id: ID of the vehicle
            parcels: List of parcels to be delivered
            vehicle_capacity: Maximum weight capacity of the vehicle
            max_distance: Maximum distance the vehicle can travel
            
        Returns:
            Route object if a valid route can be created, None otherwise
        """
        # Check if total weight exceeds vehicle capacity
        total_weight = sum(parcel.weight for parcel in parcels)
        if total_weight > vehicle_capacity:
            return None
            
        # Start building route from depot
        locations = [self.depot_location]
        current_distance = 0.0
        
        # Add delivery locations in order
        for parcel in parcels:
            # Calculate distance from last location to new delivery point
            distance_to_next = calculate_distance(
                locations[-1], 
                parcel.delivery_location
            )
            
            # Calculate distance back to depot from new point
            distance_back_to_depot = calculate_distance(
                parcel.delivery_location,
                self.depot_location
            )
            
            # Check if adding this location would exceed max distance
            if (current_distance + distance_to_next + distance_back_to_depot) > max_distance:
                return None
                
            # Add location and update distance
            locations.append(parcel.delivery_location)
            current_distance += distance_to_next
            
        # Add return to depot
        locations.append(self.depot_location)
        current_distance += calculate_distance(locations[-2], self.depot_location)
        
        # Create and return route
        route = Route(
            vehicle_id=vehicle_id,
            locations=locations,
            parcels=parcels,
            total_distance=current_distance
        )
        
        return route

    def optimize_route(self, route: Route) -> Route:
        """
        Optimize an existing route using a simple nearest neighbor approach.
        This is a basic implementation that can be extended with more sophisticated algorithms.
        
        Args:
            route: Existing route to optimize
            
        Returns:
            Optimized route
        """
        if len(route.parcels) <= 2:
            return route
            
        # Start from depot
        optimized_locations = [self.depot_location]
        unvisited_locations = route.locations[1:-1]  # Exclude depot at start and end
        current_location = self.depot_location
        
        # Build route using nearest neighbor
        while unvisited_locations:
            # Find nearest unvisited location
            nearest = min(
                unvisited_locations,
                key=lambda loc: calculate_distance(current_location, loc)
            )
            
            optimized_locations.append(nearest)
            unvisited_locations.remove(nearest)
            current_location = nearest
            
        # Return to depot
        optimized_locations.append(self.depot_location)
        
        # Create new optimized route
        optimized_route = Route(
            vehicle_id=route.vehicle_id,
            locations=optimized_locations,
            parcels=route.parcels
        )
        optimized_route.calculate_total_distance()
        
        return optimized_route