from queue import Queue
from typing import Dict
from .message_protocol import Message

class CommunicationManager:
    def __init__(self):
        self.agents = {}
        self.message_queue = Queue()
        self._running = False

    def register_agent(self, agent):
        self.agents[agent.agent_id] = agent

    def send_message(self, message: Message):
        self.message_queue.put(message)

    def start(self):
        self._running = True
        self._process_messages()

    def stop(self):
        self._running = False

    def _process_messages(self):
        while self._running:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                receiver = self.agents[message.receiver_id]
                response = receiver.process_message(message)
                if response:
                    self.send_message(response)