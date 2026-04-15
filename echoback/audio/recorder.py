import sounddevice as sd
import numpy as np
import threading
import queue
from .buffer import CircularAudioBuffer

class AudioRecorder:
    """
    Manages continuous audio recording and buffering.
    Uses callback-based recording for low latency.

    IMPORTANT: Uses WASAPI loopback to capture system audio output
    (meeting participants' voices) rather than microphone input.
    """

    def __init__(self, buffer: CircularAudioBuffer, sample_rate=16000,
                 channels=1, chunk_duration=1.0, use_loopback=True):
        self.buffer = buffer
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.blocksize = int(sample_rate * chunk_duration)
        self.use_loopback = use_loopback

        # Recording state
        self.is_recording = False
        self.stream = None
        self.chunk_queue = queue.Queue()

        # Future capture (for "next 60 seconds" after GO)
        self.future_capture_active = False
        self.future_chunks = []
        self.future_duration = 60  # seconds
        self.cancel_flag = False

    def _find_loopback_device(self):
        """
        Find WASAPI loopback device or Stereo Mix on Windows.
        Loopback devices capture system audio output (what you hear).
        """
        devices = sd.query_devices()

        print("\n🔍 Searching for system audio capture device...")

        # Priority 1: Look for WASAPI loopback device
        for idx, device in enumerate(devices):
            device_name = device['name'].lower()
            if 'loopback' in device_name and device['max_input_channels'] > 0:
                print(f"✓ Found WASAPI loopback device: {device['name']} (ID: {idx})")
                return idx

        # Priority 2: Look for Stereo Mix
        for idx, device in enumerate(devices):
            device_name = device['name'].lower()
            if 'stereo mix' in device_name and device['max_input_channels'] > 0:
                print(f"✓ Found Stereo Mix device: {device['name']} (ID: {idx})")
                return idx

        # Priority 3: Look for any device with "mix" in the name
        for idx, device in enumerate(devices):
            device_name = device['name'].lower()
            if 'mix' in device_name and device['max_input_channels'] > 0:
                print(f"⚠ Found audio mix device: {device['name']} (ID: {idx})")
                return idx

        # No loopback device found
        print("\n" + "=" * 60)
        print("⚠ WARNING: No system audio capture device found!")
        print("=" * 60)
        print("\nAvailable input devices:")
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {idx}: {device['name']}")
        print("\nTo capture meeting audio (not just microphone):")
        print("1. Right-click speaker icon in Windows taskbar")
        print("2. Select 'Sounds' → 'Recording' tab")
        print("3. Right-click → 'Show Disabled Devices'")
        print("4. Right-click 'Stereo Mix' → 'Enable'")
        print("5. Right-click 'Stereo Mix' → 'Set as Default Device'")
        print("6. Restart C3")
        print("=" * 60)
        print("\nFalling back to default input device (microphone)...\n")

        return None

    def start(self):
        """Start continuous recording"""
        if self.is_recording:
            return

        # Determine audio device
        device = None
        if self.use_loopback:
            device = self._find_loopback_device()

        self.is_recording = True
        self.stream = sd.InputStream(
            device=device,  # Use loopback device if found
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.blocksize,
            callback=self._audio_callback,
            dtype=np.int16
        )
        self.stream.start()

        # Print device info
        if device is not None:
            device_info = sd.query_devices(device)
        else:
            device_info = sd.query_devices(sd.default.device[0])

        print(f"\n✓ Recording started:")
        print(f"  Sample rate: {self.sample_rate} Hz")
        print(f"  Channels: {self.channels} (mono)")
        print(f"  Device: {device_info['name']}")
        print()

    def stop(self):
        """Stop recording"""
        if not self.is_recording:
            return

        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Recording stopped")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Called by sounddevice for each audio block.
        Runs in separate thread - must be fast!
        """
        if status:
            print(f"Audio callback status: {status}")

        # Copy audio data (indata is a view, will be reused)
        audio_chunk = indata.copy()

        # Add to circular buffer
        self.buffer.add_chunk(audio_chunk)

        # If future capture is active, also collect chunks
        if self.future_capture_active and not self.cancel_flag:
            self.future_chunks.append(audio_chunk.copy())

    def trigger_capture(self):
        """
        Trigger GO button capture:
        1. Get past 2 minutes from buffer
        2. Record next 60 seconds
        3. Return combined audio
        """
        # Reset cancel flag
        self.cancel_flag = False

        # Get past chunks
        past_chunks = self.buffer.get_all_chunks()

        # Start future capture
        self.future_capture_active = True
        self.future_chunks = []

        # Wait for future chunks (60 seconds) or until cancelled
        future_chunk_count = int(self.future_duration / self.chunk_duration)

        while len(self.future_chunks) < future_chunk_count:
            if not self.is_recording or self.cancel_flag:
                print(f"Capture stopped: recording={self.is_recording}, cancelled={self.cancel_flag}")
                break

            threading.Event().wait(0.1)  # Small sleep

        # Stop future capture
        self.future_capture_active = False

        # If cancelled, return None
        if self.cancel_flag:
            print("Capture cancelled, returning empty audio")
            return None

        # Combine past + future
        all_chunks = past_chunks + self.future_chunks

        # Concatenate into single array
        if all_chunks:
            combined_audio = np.concatenate(all_chunks)
            duration = len(combined_audio) / self.sample_rate
            print(f"Captured {duration:.1f} seconds of audio ({len(all_chunks)} chunks)")
            return combined_audio
        else:
            print("Warning: No audio chunks captured")
            return np.array([], dtype=np.int16)

    def cancel_capture(self):
        """Cancel the current capture in progress"""
        self.cancel_flag = True
        self.future_capture_active = False
        print("Cancel signal sent to recorder")

    def get_available_devices(self):
        """List available input devices"""
        return sd.query_devices()
