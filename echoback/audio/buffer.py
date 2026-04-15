from collections import deque
import numpy as np
import threading
import time

class CircularAudioBuffer:
    """
    Thread-safe circular buffer for audio chunks.
    Automatically maintains last N seconds of audio.
    """

    def __init__(self, duration_seconds=120, chunk_duration=1.0,
                 sample_rate=16000, channels=1):
        """
        Args:
            duration_seconds: Total buffer duration (default 120 = 2 minutes)
            chunk_duration: Duration of each chunk in seconds
            sample_rate: Audio sample rate (16kHz for voice)
            channels: Number of audio channels (1 = mono)
        """
        self.max_chunks = int(duration_seconds / chunk_duration)
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate
        self.channels = channels

        # Circular buffer (thread-safe deque)
        self.buffer = deque(maxlen=self.max_chunks)
        self.lock = threading.Lock()

        # Statistics
        self.total_chunks_added = 0
        self.start_time = time.time()

    def add_chunk(self, audio_data: np.ndarray):
        """Add audio chunk to buffer (called from recording thread)"""
        with self.lock:
            self.buffer.append({
                'data': audio_data.copy(),  # Copy to avoid reference issues
                'timestamp': time.time()
            })
            self.total_chunks_added += 1

    def get_all_chunks(self):
        """Get all chunks from buffer (for GO button capture)"""
        with self.lock:
            return [chunk['data'] for chunk in self.buffer]

    def clear(self):
        """Clear buffer (optional feature for pause/stop)"""
        with self.lock:
            self.buffer.clear()

    def get_stats(self):
        """Return buffer statistics"""
        with self.lock:
            return {
                'current_chunks': len(self.buffer),
                'max_chunks': self.max_chunks,
                'total_added': self.total_chunks_added,
                'uptime_seconds': time.time() - self.start_time,
                'buffer_duration_seconds': len(self.buffer) * self.chunk_duration
            }
