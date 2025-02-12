from .base_agent import BaseAgent
from ..models.route import Route

class DeliveryAgent(BaseAgent):
    def __init__(self, agent_id: str, capacity: float, max_distance: float):
        super().__init__(agent_id)
        self.capacity = capacity
        self.max_distance = max_distance
        self.current_route = None

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        if message["type"] == "CAPACITY_REQUEST":
            return {
                "type": "CAPACITY_RESPONSE",
                "agent_id": self.agent_id,
                "capacity": self.capacity,
                "max_distance": self.max_distance
            }
        return {"type": "ERROR", "message": "Unknown message type"}