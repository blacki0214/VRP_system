import unittest
from src.protocols.message_protocol import Message, MessageType  # Add this import
from src.protocols.communication_manager import CommunicationManager
from src.agents.master_routing_agent import MasterRoutingAgent
from src.agents.delivery_agent import DeliveryAgent

class TestCommunication(unittest.TestCase):
    def setUp(self):
        self.comm_manager = CommunicationManager()
        self.mra = MasterRoutingAgent("MRA_1")
        self.da1 = DeliveryAgent("DA_1", capacity=10, max_distance=100)
        
        self.comm_manager.register_agent(self.mra)
        self.comm_manager.register_agent(self.da1)

    def test_message_sending(self):
        message = Message(
            msg_type=MessageType.CAPACITY_REQUEST,
            sender_id=self.mra.agent_id,
            receiver_id=self.da1.agent_id,
            content={}
        )
        self.comm_manager.send_message(message)