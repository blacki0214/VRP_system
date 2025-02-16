import pytest
from src.protocols.communication_manager import CommunicationManager
from src.agents.master_routing_agent import MasterRoutingAgent
from src.agents.delivery_agent import DeliveryAgent
from src.protocols.message_protocol import Message, MessageType
import time

class TestCommunication:
    @pytest.fixture
    def setup_system(self):
        """Setup test system with communication manager and agents"""
        comm_manager = CommunicationManager()
        mra = MasterRoutingAgent("MRA_1")
        da1 = DeliveryAgent("DA_1", capacity=10, max_distance=100)
        da2 = DeliveryAgent("DA_2", capacity=15, max_distance=150)
        
        comm_manager.register_agent(mra)
        comm_manager.register_agent(da1)
        comm_manager.register_agent(da2)
        
        return comm_manager, mra, da1, da2

    def test_agent_registration(self, setup_system):
        """Test agent registration in communication manager"""
        comm_manager, mra, da1, da2 = setup_system
        
        assert "MRA_1" in comm_manager.agents
        assert "DA_1" in comm_manager.agents
        assert "DA_2" in comm_manager.agents

    def test_message_sending(self, setup_system):
        """Test sending messages between agents"""
        comm_manager, mra, da1, _ = setup_system
        
        message = Message(
            msg_type=MessageType.CAPACITY_REQUEST,
            sender_id=mra.agent_id,
            receiver_id=da1.agent_id,
            content={}
        )
        
        comm_manager.send_message(message)
        assert not comm_manager.message_queue.empty()

    def test_message_processing(self, setup_system):
        """Test message processing flow"""
        comm_manager, mra, da1, _ = setup_system
        comm_manager.start()
        
        message = Message(
            msg_type=MessageType.CAPACITY_REQUEST,
            sender_id=mra.agent_id,
            receiver_id=da1.agent_id,
            content={}
        )
        
        comm_manager.send_message(message)
        time.sleep(0.1)  # Wait for processing
        
        assert da1.agent_id in mra.delivery_agents
        
        comm_manager.stop()