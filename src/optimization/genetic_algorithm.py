# src/optimization/genetic_algorithm.py
import random
from typing import List, Tuple
from .base_optimizier import BaseOptimizer
from src.models.route import Route
from src.models.parcel import Parcel
from src.models.location import Location

class GeneticAlgorithm(BaseOptimizer):
    def __init__(self, population_size=100, generations=50, mutation_rate=0.1):
        super().__init__()
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def optimize(self) -> List[Route]:
        population = self._initialize_population()
        
        for generation in range(self.generations):
            fitness_scores = [self._calculate_fitness(p) for p in population]
            parents = self._selection(population, fitness_scores)
            offspring = self._crossover(parents)
            self._mutation(offspring)
            population = offspring

        return self._get_best_solution(population)

    def _create_random_solution(self) -> List[Route]:
        """Create a random solution by assigning parcels to vehicles"""
        solution = []
        available_parcels = self.parcels.copy()
        
        for vehicle_id, constraints in self.constraints['vehicle_capacities'].items():
            if not available_parcels:
                break
                
            route_parcels = []
            total_weight = 0
            random.shuffle(available_parcels)
            
            # Try to assign parcels to this vehicle
            remaining_parcels = []
            for parcel in available_parcels:
                if total_weight + parcel.weight <= constraints:
                    route_parcels.append(parcel)
                    total_weight += parcel.weight
                else:
                    remaining_parcels.append(parcel)
            
            # Create route if any parcels were assigned
            if route_parcels:
                locations = [Location(0, 0)]  # Start at warehouse
                locations.extend([p.delivery_location for p in route_parcels])
                locations.append(Location(0, 0))  # Return to warehouse
                
                route = Route(
                    vehicle_id=vehicle_id,
                    locations=locations,
                    parcels=route_parcels
                )
                route.calculate_total_distance()
                
                # Only add route if it meets distance constraint
                if route.total_distance <= self.constraints['max_distances'][vehicle_id]:
                    solution.append(route)
                    available_parcels = remaining_parcels
                else:
                    available_parcels = route_parcels + remaining_parcels
            
        return solution

    def _initialize_population(self):
        """Initialize population with random solutions"""
        return [self._create_random_solution() for _ in range(self.population_size)]

    def _calculate_fitness(self, solution: List[Route]) -> float:
        """Calculate fitness score for a solution"""
        if not self.validate_solution(solution):
            return 0.0

        total_deliveries = sum(len(route.parcels) for route in solution)
        total_distance = sum(route.total_distance for route in solution)
        
        return total_deliveries * 1000 - total_distance

    def _selection(self, population: List[List[Route]], fitness_scores: List[float]) -> List[List[Route]]:
        """Select parents using tournament selection"""
        tournament_size = 3
        parents = []
        
        for _ in range(len(population)):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            parents.append(population[winner_idx])
            
        return parents

    def _crossover(self, parents: List[List[Route]]) -> List[List[Route]]:
        """Create offspring through crossover"""
        offspring = []
        
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i + 1]
                
                # Create two children through crossover
                child1 = self._crossover_routes(parent1, parent2)
                child2 = self._crossover_routes(parent2, parent1)
                
                offspring.extend([child1, child2])
            else:
                offspring.append(parents[i])
                
        return offspring

    def _crossover_routes(self, parent1: List[Route], parent2: List[Route]) -> List[Route]:
        """Perform crossover between two parents' routes"""
        # Implement route crossover logic here
        # This is a simplified version
        crossover_point = random.randint(0, len(parent1))
        return parent1[:crossover_point] + parent2[crossover_point:]

    def _mutation(self, population: List[List[Route]]):
        """Apply mutation to the population"""
        for solution in population:
            if random.random() < self.mutation_rate:
                self._mutate_solution(solution)

    def _mutate_solution(self, solution: List[Route]):
        """Mutate a single solution"""
        if not solution:
            return
            
        # Randomly select a route to mutate
        route_idx = random.randint(0, len(solution) - 1)
        route = solution[route_idx]
        
        # Randomly swap two delivery locations
        if len(route.parcels) >= 2:
            idx1, idx2 = random.sample(range(len(route.parcels)), 2)
            route.parcels[idx1], route.parcels[idx2] = route.parcels[idx2], route.parcels[idx1]
            
            # Update locations accordingly
            locations = [Location(0, 0)]  # Warehouse
            locations.extend([p.delivery_location for p in route.parcels])
            locations.append(Location(0, 0))  # Return to warehouse
            route.locations = locations
            route.calculate_total_distance()

    def _get_best_solution(self, population: List[List[Route]]) -> List[Route]:
        """Return the best solution from the population"""
        fitness_scores = [self._calculate_fitness(solution) for solution in population]
        best_idx = fitness_scores.index(max(fitness_scores))
        return population[best_idx]