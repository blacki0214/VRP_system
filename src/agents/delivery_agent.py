from typing import Dict, Any

from .base_agent import BaseAgent
from ..models.route import Route
from typing import Dict, Any, Optional

class DeliveryAgent(BaseAgent):
    def __init__(self, agent_id: str, capacity: float, max_distance: float):
        super().__init__(agent_id)
        self.capacity = capacity
        self.max_distance = max_distance
        self.current_route: Optional[Route] = None

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process messages from MRA"""
        if message["type"] == "CAPACITY_REQUEST":
            return self._handle_capacity_request()
        elif message["type"] == "ROUTE_ASSIGNMENT":
            return self._handle_route_assignment(message["route"])
        return {"type": "ERROR", "message": "Unknown message type"}

    def _handle_capacity_request(self) -> Dict[str, Any]:
        """Handle capacity request from MRA"""
        return {
            "type": "CAPACITY_RESPONSE",
            "agent_id": self.agent_id,
            "capacity": self.capacity,
            "max_distance": self.max_distance
        }

    def _handle_route_assignment(self, route: Route) -> Dict[str, Any]:
        """Handle route assignment from MRA"""
        self.current_route = route
        return {
            "type": "ROUTE_ACCEPTED",
            "agent_id": self.agent_id
        }