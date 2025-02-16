from .base_agent import BaseAgent
from ..models.route import Route
from ..models.parcel import Parcel
from typing import Dict, List, Any

class MasterRoutingAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.delivery_agents: Dict[str, Dict[str, Any]] = {}
        self.parcels: List[Parcel] = []
        self.routes: Dict[str, Route] = {}

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process messages from DAs"""
        if message["type"] == "CAPACITY_RESPONSE":
            return self._handle_capacity_response(message)
        elif message["type"] == "ROUTE_ACCEPTED":
            return self._handle_route_acceptance(message)
        return {"type": "ERROR", "message": "Unknown message type"}

    def _handle_capacity_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capacity information from DA"""
        agent_id = message["agent_id"]
        self.delivery_agents[agent_id] = {
            "capacity": message["capacity"],
            "max_distance": message["max_distance"]
        }
        return {"type": "CAPACITY_RECEIVED", "agent_id": agent_id}

    def _handle_route_acceptance(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle route acceptance from DA"""
        agent_id = message["agent_id"]
        return {"type": "ACKNOWLEDGED", "agent_id": agent_id}

    def request_capacities(self) -> List[Dict[str, Any]]:
        """Request capacity information from all DAs"""
        return [
            {
                "type": "CAPACITY_REQUEST",
                "target_agent": agent_id
            }
            for agent_id in self.delivery_agents.keys()
        ]