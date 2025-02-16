
from typing import Dict, List, Optional, Any  # Added Any import
from .base_agent import BaseAgent
from src.protocols.message_protocol import Message, MessageType

class MasterRoutingAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.delivery_agents: Dict[str, Dict[str, Any]] = {}
        self.message_handler = self._setup_handlers()

    def _setup_handlers(self):
        handlers = {
            MessageType.CAPACITY_RESPONSE: self._handle_capacity_response,
            MessageType.ROUTE_CONFIRMATION: self._handle_route_confirmation
        }
        return handlers

    def process_message(self, message: Message) -> Optional[Message]:
        if message.msg_type in self.message_handler:
            return self.message_handler[message.msg_type](message)
        return None

    def _handle_capacity_response(self, message: Message) -> Optional[Message]:
        agent_id = message.sender_id
        self.delivery_agents[agent_id] = {
            "capacity": message.content["capacity"],
            "max_distance": message.content["max_distance"]
        }
        return None
    
    def _handle_route_confirmation(self, message: Message) -> Optional[Message]:
        """Handle route confirmation messages from Delivery Agents"""
        agent_id = message.sender_id
        status = message.content["status"]

        if status == "accepted":
            # Update agent's status with assigned route
            self.delivery_agents[agent_id]["current_route"] = message.content.get("route")
            return None
        elif status == "rejected":
            # Handle rejection - could implement reassignment logic here
            reason = message.content.get("reason", "Unknown reason")
            self.delivery_agents[agent_id]["route_status"] = f"Rejected: {reason}"
            return None
        else:
            # Handle unknown status
            return Message(
                msg_type=MessageType.ERROR,
                sender_id=self.agent_id,
                receiver_id=agent_id,
                content={"error": "Invalid route confirmation status"}
            )