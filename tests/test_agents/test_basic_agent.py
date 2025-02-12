import unittest
from src.agents.delivery_agent import DeliveryAgent
from src.agents.master_routing_agent import MasterRoutingAgent
from src.models.location import Location
from src.models.parcel import Parcel
from src.models.route import Route


class TestAgentCommunication(unittest.TestCase):
    def setUp(self):
        # Create agents
        self.mra = MasterRoutingAgent("MRA_1")
        self.da = DeliveryAgent("DA_1", capacity=10, max_distance=100)

    def test_capacity_request(self):
        # Test capacity request/response
        request = {"type": "CAPACITY_REQUEST"}
        response = self.da.process_message(request)

        self.assertEqual(response["type"], "CAPACITY_RESPONSE")
        self.assertEqual(response["capacity"], 10)
        self.assertEqual(response["max_distance"], 100)

    def test_route_assignment(self):
        # Create test route
        route = Route(
            vehicle_id="DA_1",
            locations=[Location(0, 0), Location(1, 1)],
            parcels=[Parcel(1, Location(1, 1))],
            total_distance=1.414
        )

        # Test route assignment
        request = {"type": "ROUTE_ASSIGNMENT", "route": route}
        response = self.da.process_message(request)

        self.assertEqual(response["type"], "ROUTE_ACCEPTED")
        self.assertEqual(response["agent_id"], "DA_1")


if __name__ == '__main__':
    unittest.main()