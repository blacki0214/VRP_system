class MasterRoutingAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.delivery_agents = {}
        self.parcels = []
        self.message_handler = MessageHandler()  # New: Added message handler
        self._setup_handlers()  # New: Setup message handlers

    def _setup_handlers(self):  # New: Handler registration
        self.message_handler.register_handler(
            MessageType.CAPACITY_RESPONSE,
            self._handle_capacity_response
        )
        self.message_handler.register_handler(
            MessageType.ROUTE_CONFIRMATION,
            self._handle_route_confirmation
        )

    def assign_routes(self):  # New: Route assignment functionality
        """Route assignment logic"""
        optimized_routes = self._optimize_routes()
        for da_id, route in optimized_routes.items():
            self._assign_route(da_id, route)