# src/optimization/route_optimizer_ga.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import List, Dict, Tuple, Optional, Callable
from datetime import datetime
import numpy as np
from src.models.route import Route
from src.models.location import Location
from src.models.parcel import Parcel
from src.data.data_processor import DataProcessor

class RouteOptimizerGA:
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
        self.warehouse_location = self._get_warehouse_location()
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elitism_count = 5
        self.best_solution: List[Route] = []
        self.best_fitness = 0.0

    def optimize(self) -> List[Route]:
        """Main GA optimization method"""
        print("\nInitializing Genetic Algorithm optimization...")
        
        # Create initial population
        population = self._initialize_population()
        
        # Evaluate initial population
        fitness_scores = [self._calculate_fitness(solution) for solution in population]
        
        # Track best solution
        best_idx = fitness_scores.index(max(fitness_scores))
        self.best_solution = copy.deepcopy(population[best_idx])
        self.best_fitness = fitness_scores[best_idx]
        
        print(f"Initial best fitness: {self.best_fitness:.4f}")
        
        # Main GA loop
        for generation in range(self.generations):
            # Selection
            selected = self._selection(population, fitness_scores)
            
            # Create new population
            new_population = []
            
            # Elitism - keep best solutions
            sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
            for i in range(self.elitism_count):
                new_population.append(copy.deepcopy(population[sorted_indices[i]]))
            
            # Crossover and Mutation
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = selected[random.randint(0, len(selected) - 1)]
                parent2 = selected[random.randint(0, len(selected) - 1)]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    offspring = self._crossover(parent1, parent2)
                else:
                    offspring = copy.deepcopy(parent1)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    offspring = self._mutate(offspring)
                
                # Repair solution if needed
                offspring = self._repair_solution(offspring)
                
                # Add to new population
                new_population.append(offspring)
            
            # Update population
            population = new_population[:self.population_size]
            
            # Evaluate new population
            fitness_scores = [self._calculate_fitness(solution) for solution in population]
            
            # Update best solution
            current_best_idx = fitness_scores.index(max(fitness_scores))
            if fitness_scores[current_best_idx] > self.best_fitness:
                self.best_solution = copy.deepcopy(population[current_best_idx])
                self.best_fitness = fitness_scores[current_best_idx]
                print(f"Generation {generation+1}: New best fitness: {self.best_fitness:.4f}")
            
            # Progress reporting
            if (generation + 1) % 10 == 0:
                print(f"Generation {generation+1}/{self.generations} completed. Best fitness: {self.best_fitness:.4f}")
        
        print(f"\nGA optimization completed. Final best fitness: {self.best_fitness:.4f}")
        evaluation = self.evaluate_solution(self.best_solution)
        print(f"Parcels delivered: {evaluation['parcels_delivered']}")
        print(f"Total cost: ${evaluation['total_cost']:.2f}")
        
        return self.best_solution

    def _initialize_population(self) -> List[List[Route]]:
        """Initialize population with diverse solutions"""
        population = []
        
        for _ in range(self.population_size):
            # Create a solution with randomization
            solution = self._create_randomized_solution()
            population.append(solution)
        
        return population

    def _create_randomized_solution(self) -> List[Route]:
        """Create a solution with randomized order assignments"""
        routes = []
        truck_types = ['9.6', '12.5', '16.5']
        
        # Get all order IDs and shuffle them
        all_orders = list(self.data_processor.time_windows.keys())
        random.shuffle(all_orders)
        
        unassigned_orders = all_orders.copy()
        
        # Create routes until all orders are assigned or no more can be assigned
        while unassigned_orders:
            # Randomly select truck type with probabilities favoring smaller trucks
            probabilities = [0.5, 0.3, 0.2]  # 50% small, 30% medium, 20% large
            truck_type = random.choices(truck_types, probabilities)[0]
            
            route = self._build_route(truck_type, unassigned_orders, randomize=True)
            
            if route and route.parcels:
                routes.append(route)
                # Remove assigned orders
                assigned_ids = [parcel.id for parcel in route.parcels]
                unassigned_orders = [order_id for order_id in unassigned_orders 
                                   if int(order_id) not in assigned_ids]
            else:
                # If we couldn't create a route, drop a random order
                if unassigned_orders:
                    idx = random.randint(0, len(unassigned_orders) - 1)
                    unassigned_orders.pop(idx)
        
        return routes

    def _build_route(self, truck_type: str, available_orders: List[str], randomize: bool = False) -> Optional[Route]:
        """Build a feasible route for the given truck type with optional randomization"""
        # Initialize an empty route
        vehicle_id = f"V_{truck_type}_{random.randint(0, 999)}"
        route = Route(
            vehicle_id=vehicle_id,
            locations=[self.warehouse_location],
            parcels=[]
        )
        
        # Get truck capacity
        capacity = self.data_processor.truck_specifications[truck_type]['weight_capacity']
        remaining_capacity = capacity
        
        # Process orders in random order if randomize=True
        orders_to_process = available_orders.copy()
        if randomize:
            random.shuffle(orders_to_process)
        
        # Try to add orders
        for order_id in orders_to_process:
            order_data = self.data_processor.time_windows[order_id]
            
            # Create locations
            source_loc = self._create_location(order_data['source'])
            dest_loc = self._create_location(order_data['destination'])
            
            # Create parcel
            parcel = Parcel(
                id=int(order_id),
                delivery_location=dest_loc,
                weight=order_data['weight']
            )
            
            # Skip if weight exceeds capacity
            if parcel.weight > remaining_capacity:
                continue
            
            # Add to route
            temp_locations = route.locations.copy()
            if temp_locations[-1] != source_loc:
                temp_locations.append(source_loc)
            temp_locations.append(dest_loc)
            
            # Check feasibility
            temp_route = Route(
                vehicle_id=vehicle_id,
                locations=temp_locations,
                parcels=route.parcels + [parcel]
            )
            temp_route.calculate_total_distance()
            
            is_feasible, _ = self._check_route_feasibility(temp_route, truck_type)
            
            if is_feasible:
                route.locations = temp_locations
                route.parcels.append(parcel)
                remaining_capacity -= parcel.weight
        
        # Complete route
        if route.parcels:
            if route.locations[-1] != self.warehouse_location:
                route.locations.append(self.warehouse_location)
            
            route.calculate_total_distance()
            route.total_cost = route.total_distance * \
                self.data_processor.truck_specifications[truck_type]['cost_per_km']
            
            route.is_feasible, route.violation_reason = self._check_route_feasibility(
                route, truck_type
            )
            
            return route
        
        return None

    def _calculate_fitness(self, solution: List[Route]) -> float:
        """Calculate fitness score for a solution"""
        evaluation = self.evaluate_solution(solution)
        
        # Multi-objective fitness
        parcels_weight = 0.6  # Prioritize delivering parcels
        cost_weight = 0.3     # Minimize cost
        route_weight = 0.1    # Minimize number of routes
        
        # Normalize values
        max_parcels = len(self.data_processor.time_windows)
        max_cost = 100000  # Some large value for normalization
        max_routes = max_parcels  # Worst case: one route per parcel
        
        parcels_score = evaluation['parcels_delivered'] / max_parcels
        cost_score = 1 - (min(evaluation['total_cost'], max_cost) / max_cost)
        route_score = 1 - (evaluation['num_routes'] / max_routes)
        
        # Calculate weighted fitness
        fitness = (parcels_weight * parcels_score) + \
                 (cost_weight * cost_score) + \
                 (route_weight * route_score)
        
        return fitness

    def _selection(self, population: List[List[Route]], fitness_scores: List[float]) -> List[List[Route]]:
        """Tournament selection for parent selection"""
        selected = []
        tournament_size = 3
        
        for _ in range(self.population_size):
            # Select random individuals for tournament
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Select winner (highest fitness)
            winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            selected.append(copy.deepcopy(population[winner_idx]))
        
        return selected

    def _crossover(self, parent1: List[Route], parent2: List[Route]) -> List[Route]:
        """Route-based crossover operator"""
        # Start with empty solution
        offspring = []
        
        # Track assigned orders
        assigned_orders = set()
        
        # Randomly select routes from both parents
        all_routes = parent1 + parent2
        random.shuffle(all_routes)
        
        for route in all_routes:
            # Check if route has orders not yet assigned
            route_order_ids = {parcel.id for parcel in route.parcels}
            if not route_order_ids.issubset(assigned_orders):
                # Create a new route with only unassigned orders
                new_route = self._create_route_with_orders(
                    route.vehicle_id.split('_')[1],  # Truck type
                    [str(order_id) for order_id in route_order_ids if order_id not in assigned_orders]
                )
                
                if new_route and new_route.parcels:
                    offspring.append(new_route)
                    # Update assigned orders
                    assigned_orders.update(parcel.id for parcel in new_route.parcels)
        
        return offspring

    def _create_route_with_orders(self, truck_type: str, order_ids: List[str]) -> Optional[Route]:
        """Create a route with specified orders"""
        vehicle_id = f"V_{truck_type}_{random.randint(0, 999)}"
        route = Route(
            vehicle_id=vehicle_id,
            locations=[self.warehouse_location],
            parcels=[]
        )
        
        capacity = self.data_processor.truck_specifications[truck_type]['weight_capacity']
        remaining_capacity = capacity
        
        for order_id in order_ids:
            if order_id not in self.data_processor.time_windows:
                continue
                
            order_data = self.data_processor.time_windows[order_id]
            source_loc = self._create_location(order_data['source'])
            dest_loc = self._create_location(order_data['destination'])
            
            parcel = Parcel(
                id=int(order_id),
                delivery_location=dest_loc,
                weight=order_data['weight']
            )
            
            if parcel.weight > remaining_capacity:
                continue
            
            # Add to route
            if route.locations[-1] != source_loc:
                route.locations.append(source_loc)
            route.locations.append(dest_loc)
            route.parcels.append(parcel)
            remaining_capacity -= parcel.weight
        
        # Complete route
        if route.parcels:
            if route.locations[-1] != self.warehouse_location:
                route.locations.append(self.warehouse_location)
                
            route.calculate_total_distance()
            route.total_cost = route.total_distance * \
                self.data_processor.truck_specifications[truck_type]['cost_per_km']
            
            route.is_feasible, route.violation_reason = self._check_route_feasibility(
                route, truck_type
            )
            
            return route
        
        return None

    def _mutate(self, solution: List[Route]) -> List[Route]:
        """Apply mutation operators to a solution"""
        if not solution:
            return solution
            
        # Apply a random mutation operator
        mutation_operators = [
            self._swap_orders_mutation,
            self._change_truck_mutation,
            self._reorder_stops_mutation
        ]
        
        operator = random.choice(mutation_operators)
        return operator(solution)

    def _swap_orders_mutation(self, solution: List[Route]) -> List[Route]:
        """Swap orders between two routes"""
        if len(solution) < 2:
            return solution
            
        # Select two random routes
        idx1, idx2 = random.sample(range(len(solution)), 2)
        route1, route2 = solution[idx1], solution[idx2]
        
        # Both routes must have at least one parcel
        if not route1.parcels or not route2.parcels:
            return solution
            
        # Select random parcels to swap
        parcel1 = random.choice(route1.parcels)
        parcel2 = random.choice(route2.parcels)
        
        # Create new routes without the selected parcels
        new_route1 = self._create_route_without_parcel(route1, parcel1.id)
        new_route2 = self._create_route_without_parcel(route2, parcel2.id)
        
        # Add the swapped parcels if possible
        order_id1, order_id2 = str(parcel1.id), str(parcel2.id)
        
        truck_type1 = route1.vehicle_id.split('_')[1]
        truck_type2 = route2.vehicle_id.split('_')[1]
        
        # Try to add parcel2 to route1
        if new_route1:
            result1 = self._add_order_to_route(new_route1, order_id2, truck_type1)
            if result1:
                solution[idx1] = result1
            
        # Try to add parcel1 to route2
        if new_route2:
            result2 = self._add_order_to_route(new_route2, order_id1, truck_type2)
            if result2:
                solution[idx2] = result2
        
        return solution

    def _create_route_without_parcel(self, route: Route, parcel_id: int) -> Optional[Route]:
        """Create a new route excluding a specific parcel"""
        # Get orders except the one to exclude
        order_ids = [str(parcel.id) for parcel in route.parcels if parcel.id != parcel_id]
        
        if not order_ids:
            return None
            
        truck_type = route.vehicle_id.split('_')[1]
        return self._create_route_with_orders(truck_type, order_ids)

    def _add_order_to_route(self, route: Route, order_id: str, truck_type: str) -> Optional[Route]:
        """Try to add an order to an existing route"""
        if order_id not in self.data_processor.time_windows:
            return route
            
        order_data = self.data_processor.time_windows[order_id]
        source_loc = self._create_location(order_data['source'])
        dest_loc = self._create_location(order_data['destination'])
        
        parcel = Parcel(
            id=int(order_id),
            delivery_location=dest_loc,
            weight=order_data['weight']
        )
        
        # Check capacity
        current_weight = sum(p.weight for p in route.parcels)
        capacity = self.data_processor.truck_specifications[truck_type]['weight_capacity']
        
        if current_weight + parcel.weight > capacity:
            return route
        
        # Create new route with added parcel
        new_locations = route.locations[:-1]  # Remove warehouse return
        
        # Add new locations
        if new_locations[-1] != source_loc:
            new_locations.append(source_loc)
        new_locations.append(dest_loc)
        new_locations.append(self.warehouse_location)  # Add warehouse return
        
        new_route = Route(
            vehicle_id=route.vehicle_id,
            locations=new_locations,
            parcels=route.parcels + [parcel]
        )
        
        new_route.calculate_total_distance()
        new_route.total_cost = new_route.total_distance * \
            self.data_processor.truck_specifications[truck_type]['cost_per_km']
        
        is_feasible, _ = self._check_route_feasibility(new_route, truck_type)
        
        if is_feasible:
            return new_route
        
        return route

    def _change_truck_mutation(self, solution: List[Route]) -> List[Route]:
        """Change truck type for a random route"""
        if not solution:
            return solution
            
        # Select a random route
        route_idx = random.randint(0, len(solution) - 1)
        route = solution[route_idx]
        
        # Get current truck type
        current_type = route.vehicle_id.split('_')[1]
        
        # Select a different truck type
        truck_types = ['9.6', '12.5', '16.5']
        truck_types.remove(current_type)
        new_type = random.choice(truck_types)
        
        # Create a new route with the same orders but different truck type
        order_ids = [str(parcel.id) for parcel in route.parcels]
        new_route = self._create_route_with_orders(new_type, order_ids)
        
        if new_route and new_route.is_feasible:
            solution[route_idx] = new_route
        
        return solution

    def _reorder_stops_mutation(self, solution: List[Route]) -> List[Route]:
        """Reorder the stops within a route"""
        if not solution:
            return solution
            
        # Select a random route
        route_idx = random.randint(0, len(solution) - 1)
        route = solution[route_idx]
        
        if len(route.parcels) < 2:
            return solution
            
        # Get the order IDs
        order_ids = [str(parcel.id) for parcel in route.parcels]
        random.shuffle(order_ids)
        
        # Recreate the route with reordered stops
        truck_type = route.vehicle_id.split('_')[1]
        new_route = self._create_route_with_orders(truck_type, order_ids)
        
        if new_route and new_route.is_feasible:
            solution[route_idx] = new_route
        
        return solution

    def _repair_solution(self, solution: List[Route]) -> List[Route]:
        """Repair infeasible solutions"""
        # Remove any infeasible routes
        solution = [route for route in solution if route.is_feasible]
        
        # Check for duplicate orders
        assigned_orders = set()
        repaired_solution = []
        
        for route in solution:
            # Create a new route with only orders not yet assigned
            new_order_ids = []
            for parcel in route.parcels:
                if parcel.id not in assigned_orders:
                    new_order_ids.append(str(parcel.id))
                    assigned_orders.add(parcel.id)
            
            if new_order_ids:
                truck_type = route.vehicle_id.split('_')[1]
                new_route = self._create_route_with_orders(truck_type, new_order_ids)
                if new_route and new_route.is_feasible and new_route.parcels:
                    repaired_solution.append(new_route)
        
        return repaired_solution

    def _check_route_feasibility(self, route: Route, truck_type: str) -> Tuple[bool, str]:
        """Check if route meets all constraints"""
        # Check capacity
        total_weight = route.get_total_weight()
        capacity = self.data_processor.truck_specifications[truck_type]['weight_capacity']
        
        if total_weight > capacity:
            return False, f"Capacity exceeded: {total_weight} > {capacity}"
        
        # Check maximum distance constraint
        max_distance = 5000  # Example value
        if route.total_distance > max_distance:
            return False, f"Distance exceeded: {route.total_distance} > {max_distance}"
        
        return True, "Route is feasible"

    def _get_warehouse_location(self) -> Location:
        """Get warehouse location (assuming first city is warehouse)"""
        warehouse_city = list(self.data_processor.cities)[0]
        return self._create_location(warehouse_city)

    def _create_location(self, city_name: str) -> Location:
        """Create Location object from city name"""
        if not hasattr(self, '_location_cache'):
            self._location_cache = {}
            
        if city_name not in self._location_cache:
            idx = self.data_processor.city_to_idx.get(city_name, 0)
            self._location_cache[city_name] = Location(idx, idx)
            
        return self._location_cache[city_name]

    def evaluate_solution(self, routes: List[Route]) -> Dict:
        """Evaluate solution quality"""
        # Count total parcels delivered
        parcels_delivered = sum(len(route.parcels) for route in routes if route.is_feasible)
        
        # Calculate total cost
        total_cost = sum(route.total_cost for route in routes if route.is_feasible)
        
        # Calculate total distance
        total_distance = sum(route.total_distance for route in routes if route.is_feasible)
        
        # Count infeasible routes
        infeasible_routes = sum(1 for route in routes if not route.is_feasible)
        
        return {
            'parcels_delivered': parcels_delivered,
            'total_cost': total_cost,
            'total_distance': total_distance,
            'num_routes': len(routes),
            'infeasible_routes': infeasible_routes
        }

def main():
    """Test the GA route optimizer"""
    try:
        from src.data.data_processor import DataProcessor
        
        # Initialize data
        processor = DataProcessor()
        processor.load_data('distance.csv', 'order_large.csv')
        processor._create_distance_matrix()
        processor._process_time_windows()
        
        # Create optimizer
        optimizer = RouteOptimizerGA(processor)
        
        # Run optimization
        solution = optimizer.optimize()
        
        # Print solution details
        if solution:
            print("\nBest Solution Details:")
            for i, route in enumerate(solution):
                print(f"\nRoute {i+1} ({route.vehicle_id}):")
                print(f"Parcels: {len(route.parcels)}")
                print(f"Distance: {route.total_distance:.2f} km")
                print(f"Cost: ${route.total_cost:.2f}")
                print(f"Load: {route.get_total_weight():.2f} kg")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


