import numpy as np
import wave
import json
import threading
from datetime import datetime
from pathlib import Path

class SaveManager:
    """Manages saving captured audio to files"""

    def __init__(self, recordings_dir="recordings"):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)

        self.sample_rate = 16000
        self.channels = 1
        self.sampwidth = 2  # 16-bit = 2 bytes

    def save_capture(self, audio_data: np.ndarray, tags="", meeting_app=None):
        """
        Save captured audio in background thread.

        Args:
            audio_data: numpy array of audio samples (int16)
            tags: Optional user tags/notes
            meeting_app: Detected meeting app (future feature)
        """
        # Generate filename with timestamp
        timestamp = datetime.now()
        filename_base = timestamp.strftime("%Y-%m-%d_%H%M%S")

        # Launch save thread (don't block UI)
        save_thread = threading.Thread(
            target=self._save_thread,
            args=(audio_data, filename_base, tags, meeting_app, timestamp),
            daemon=True
        )
        save_thread.start()

        return filename_base

    def _save_thread(self, audio_data, filename_base, tags, meeting_app, timestamp):
        """Background thread for file I/O"""
        try:
            # Save WAV file
            wav_path = self.recordings_dir / f"{filename_base}.wav"
            with wave.open(str(wav_path), 'w') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.sampwidth)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())

            # Calculate duration
            duration_seconds = len(audio_data) / self.sample_rate
            file_size_mb = wav_path.stat().st_size / (1024 * 1024)

            # Save metadata
            metadata = {
                "timestamp": timestamp.isoformat(),
                "duration_seconds": duration_seconds,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "format": "wav",
                "file_size_mb": round(file_size_mb, 2),
                "tags": tags,
                "meeting_app": meeting_app
            }

            json_path = self.recordings_dir / f"{filename_base}.json"
            with open(json_path, 'w') as json_file:
                json.dump(metadata, json_file, indent=2)

            print(f"✓ Saved: {wav_path.name} ({duration_seconds:.1f}s, {file_size_mb:.1f}MB)")

        except Exception as e:
            print(f"✗ Save error: {e}")
