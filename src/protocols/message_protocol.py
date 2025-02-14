# src/protocols/message_protocol.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class MessageType(Enum):
    CAPACITY_REQUEST = "CAPACITY_REQUEST"
    CAPACITY_RESPONSE = "CAPACITY_RESPONSE"
    ROUTE_ASSIGNMENT = "ROUTE_ASSIGNMENT"
    ROUTE_CONFIRMATION = "ROUTE_CONFIRMATION"
    ERROR = "ERROR"

@dataclass
class Message:
    msg_type: MessageType
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]
    conversation_id: Optional[str] = None