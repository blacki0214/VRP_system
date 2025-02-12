import unittest
from src.agents.delivery_agent import DeliveryAgent
from src.agents.master_routing_agent import MasterRoutingAgent

class TestAgentCommunication(unittest.TestCase):
    def setUp(self):
        self.mra = MasterRoutingAgent("MRA_1")
        self.da = DeliveryAgent("DA_1", capacity=10, max_distance=100)

    def test_capacity_request(self):
        request = {"type": "CAPACITY_REQUEST"}
        response = self.da.process_message(request)
        self.assertEqual(response["type"], "CAPACITY_RESPONSE")
        self.assertEqual(response["capacity"], 10)

if __name__ == '__main__':
    unittest.main()