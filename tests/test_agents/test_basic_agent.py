import unittest
from src.protocols.message_protocol import Message, MessageType  # Add this import
from src.agents.delivery_agent import DeliveryAgent
from src.agents.master_routing_agent import MasterRoutingAgent

class TestAgentCommunication(unittest.TestCase):
    def setUp(self):
        self.mra = MasterRoutingAgent("MRA_1")
        self.da = DeliveryAgent("DA_1", capacity=10, max_distance=100)

    def test_capacity_request(self):
        # Create a capacity request message
        message = Message(
            msg_type=MessageType.CAPACITY_REQUEST,
            sender_id=self.mra.agent_id,
            receiver_id=self.da.agent_id,
            content={}
        )
        response = self.da.process_message(message)
        self.assertEqual(response.msg_type, MessageType.CAPACITY_RESPONSE)
        self.assertEqual(response.content["capacity"], 10)