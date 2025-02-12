from .base_agent import BaseAgent
from ..models.route import Route
from typing import Dict, List

class MasterRoutingAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.delivery_agents: Dict[str, Dict[str, Any]] = {}
        self.parcels: List[Parcel] = []

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if message["type"] == "CAPACITY_RESPONSE":
            return self._handle_capacity_response(message)
        return {"type": "ERROR", "message": "Unknown message type"}

    def _handle_capacity_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = message["agent_id"]
        self.delivery_agents[agent_id] = {
            "capacity": message["capacity"],
            "max_distance": message["max_distance"]
        }
        return {"type": "CAPACITY_RECEIVED"};