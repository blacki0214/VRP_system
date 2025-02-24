import pytest
from src.models.location import Location
from src.models.parcel import Parcel
from src.utils.route_creator import RouteCreator

class TestRouteCreator:
    @pytest.fixture
    def setup_creator(self):
        """Setup test route creator with depot at origin"""
        depot = Location(0, 0)
        return RouteCreator(depot)
        
    @pytest.fixture
    def sample_parcels(self):
        """Create sample parcels for testing"""
        return [
            Parcel(id=1, delivery_location=Location(1, 1), weight=2.0),
            Parcel(id=2, delivery_location=Location(2, 2), weight=3.0),
            Parcel(id=3, delivery_location=Location(3, 3), weight=1.0)
        ]

    def test_route_creation_success(self, setup_creator, sample_parcels):
        """Test successful route creation"""
        creator = setup_creator
        
        route = creator.create_route(
            vehicle_id="V1",
            parcels=sample_parcels,
            vehicle_capacity=10.0,
            max_distance=20.0
        )
        
        assert route is not None
        assert route.vehicle_id == "V1"
        assert len(route.locations) == len(sample_parcels) + 2  # Including depot at start and end
        assert route.total_distance > 0
        assert route.get_total_weight() == 6.0  # Sum of all parcel weights

    def test_route_creation_capacity_exceeded(self, setup_creator, sample_parcels):
        """Test route creation when capacity is exceeded"""
        creator = setup_creator
        
        route = creator.create_route(
            vehicle_id="V1",
            parcels=sample_parcels,
            vehicle_capacity=5.0,  # Less than total parcel weight
            max_distance=20.0
        )
        
        assert route is None

    def test_route_creation_distance_exceeded(self, setup_creator, sample_parcels):
        """Test route creation when max distance is exceeded"""
        creator = setup_creator
        
        route = creator.create_route(
            vehicle_id="V1",
            parcels=sample_parcels,
            vehicle_capacity=10.0,
            max_distance=2.0  # Very short max distance
        )
        
        assert route is None

    def test_route_optimization(self, setup_creator):
        """Test route optimization"""
        creator = setup_creator
        
        # Create a deliberately inefficient route
        parcels = [
            Parcel(id=1, delivery_location=Location(1, 1), weight=1.0),
            Parcel(id=2, delivery_location=Location(1, 2), weight=1.0),
            Parcel(id=3, delivery_location=Location(1, 3), weight=1.0),
        ]
        
        original_route = creator.create_route(
            vehicle_id="V1",
            parcels=parcels,
            vehicle_capacity=10.0,
            max_distance=20.0
        )
        
        optimized_route = creator.optimize_route(original_route)
        
        assert optimized_route.total_distance <= original_route.total_distance
        assert len(optimized_route.locations) == len(original_route.locations)
        assert optimized_route.parcels == original_route.parcels

    def test_single_delivery_route(self, setup_creator):
        """Test route creation with single delivery"""
        creator = setup_creator
        parcels = [Parcel(id=1, delivery_location=Location(1, 1), weight=2.0)]
        
        route = creator.create_route(
            vehicle_id="V1",
            parcels=parcels,
            vehicle_capacity=10.0,
            max_distance=20.0
        )
        
        assert route is not None
        assert len(route.locations) == 3  # Depot -> Delivery -> Depot
        assert route.parcels == parcels

    def test_empty_route(self, setup_creator):
        """Test route creation with no parcels"""
        creator = setup_creator
        
        route = creator.create_route(
            vehicle_id="V1",
            parcels=[],
            vehicle_capacity=10.0,
            max_distance=20.0
        )
        
        assert route is not None
        assert len(route.locations) == 2  # Just depot at start and end
        assert route.total_distance == 0
        assert route.get_total_weight() == 0