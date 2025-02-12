from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        pass