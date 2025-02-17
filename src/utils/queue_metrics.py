
import time
from collections import deque
from typing import Deque, Tuple

class QueueRateTracker:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size  # Window size in seconds
        self.message_timestamps: Deque[float] = deque()
        self.start_time = time.time()

    def record_message(self):
        """Record a message being processed"""
        current_time = time.time()
        self.message_timestamps.append(current_time)
        
        # Remove timestamps older than window_size
        while (self.message_timestamps and 
               current_time - self.message_timestamps[0] > self.window_size):
            self.message_timestamps.popleft()

    def get_current_rate(self) -> float:
        """Calculate current processing rate (messages/second)"""
        if not self.message_timestamps:
            return 0.0
            
        current_time = time.time()
        window_start = current_time - self.window_size
        
        # Count messages in current window
        messages_in_window = sum(1 for t in self.message_timestamps 
                               if t > window_start)
        
        return messages_in_window / self.window_size

    def get_rate_statistics(self) -> Tuple[float, float, float]:
        """Get min, max, and average rates"""
        if not self.message_timestamps:
            return 0.0, 0.0, 0.0
            
        total_time = time.time() - self.start_time
        total_messages = len(self.message_timestamps)
        
        return (
            self.get_current_rate(),  # Current rate
            total_messages / total_time,  # Average rate
            max(1, total_messages) / min(total_time, self.window_size)  # Peak rate
        )