class DeliveryAgent:
    def __init__(self, agent_id: str, capacity: float, max_distance: float):
        self.agent_id = agent_id
        self.capacity = capacity
        self.max_distance = max_distance
        self.current_route = None
        self.message_handler = MessageHandler()
        self._setup_handlers()

    def _setup_handlers(self):
        self.message_handler.register_handler(
            MessageType.CAPACITY_REQUEST,
            self._handle_capacity_request
        )
        self.message_handler.register_handler(
            MessageType.ROUTE_ASSIGNMENT,
            self._handle_route_assignment
        )

    def _handle_route_assignment(self, message: Message) -> Message:
        route = message.content["route"]
        if self._validate_route(route):
            self.current_route = route
            return Message(
                msg_type=MessageType.ROUTE_CONFIRMATION,
                sender_id=self.agent_id,
                receiver_id=message.sender_id,
                content={"status": "ACCEPTED"}
            )
        return Message(
            msg_type=MessageType.ROUTE_CONFIRMATION,
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            content={
                "status": "REJECTED",
                "reason": "Route violates constraints"
            }
        )