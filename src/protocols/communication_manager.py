from queue import Queue
from typing import Dict
from .message_protocol import Message
from src.utils.performance_metrics import MessageTimeTracker
from src.utils.queue_metrics import QueueRateTracker
from src.utils.memory_metrics import MemoryTracker

class CommunicationManager:
    def __init__(self):
        self.message_tracker = MessageTimeTracker()
        self.queue_tracker = QueueRateTracker()
        self.memory_tracker = MemoryTracker()

        self.agents = {}
        self.message_queue = Queue()
        self._running = False



    def register_agent(self, agent):
        self.agents[agent.agent_id] = agent

    def send_message(self, message: Message):
        self.message_queue.put(message)
        self.queue_tracker.record_message()

    def start(self):
        self._running = True
        self.memory_tracker.take_snapshot()
        self._process_messages()

    def stop(self):
        self._running = False

    def process_message(self, message):  # Add this public method
        """Process a single message"""
        start_time = self.message_tracker.start_tracking()

        #Take memory snapshot
        self.memory_tracker.take_snapshot()

        #Process message
        receiver = self.agents[message.receiver_id]
        response = receiver.process_message(message)

        #Record metrics
        self.message_tracker.stop_tracking(start_time, message.msg_type.value)
        self.queue_tracker.record_message()

        return response

    def _process_messages(self):  # Keep the internal method
        """Internal method to process messages from queue"""
        while self._running:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                response = self.process_message(message)
                if response:
                    self.send_message(response)


    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        current_rate, avg_rate, peak_rate = self.queue_tracker.get_rate_statistics()
        memory_stats = self.memory_tracker.get_memory_statistics()
        memory_trend = self.memory_tracker.get_memory_trend()
        
        return {
            'message_processing': {
                'average_time': self.message_tracker.get_average_processing_time(),
                'by_type': self.message_tracker.get_metrics_by_type()
            },
            'queue_processing': {
                'current_rate': current_rate,
                'average_rate': avg_rate,
                'peak_rate': peak_rate
            },
            'memory_usage': {
                'statistics': memory_stats,
                'trend': memory_trend
            }
        }

    def print_performance_metrics(self):
        """Print current performance metrics"""
        metrics = self.get_performance_metrics()
        print("\n=== Performance Metrics ===")
        print(f"Message Processing:")
        print(f"  Average Time: {metrics['message_processing']['average_time']:.2f}ms")
        print(f"\nQueue Processing:")
        print(f"  Current Rate: {metrics['queue_processing']['current_rate']:.2f} msgs/sec")
        print(f"  Average Rate: {metrics['queue_processing']['average_rate']:.2f} msgs/sec")
        print(f"\nMemory Usage:")
        print(f"  Current: {metrics['memory_usage']['statistics']['rss']['current']:.2f} MB")
        print(f"  Peak: {metrics['memory_usage']['statistics']['rss']['peak']:.2f} MB")