import unittest
from src.protocols.message_protocol import Message, MessageType  # Add this import
from src.agents.delivery_agent import DeliveryAgent
from src.models.route import Route
from src.models.location import Location

class TestDeliveryAgent(unittest.TestCase):
    def setUp(self):
        self.da = DeliveryAgent("DA_1", capacity=10, max_distance=100)

    def test_capacity_request_handling(self):
        message = Message(
            msg_type=MessageType.CAPACITY_REQUEST,
            sender_id="MRA_1",
            receiver_id=self.da.agent_id,
            content={}
        )
        response = self.da.process_message(message)
        self.assertEqual(response.msg_type, MessageType.CAPACITY_RESPONSE)