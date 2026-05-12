"""
Audio stream management for real-time speech processing.
"""
import pyaudio
import queue
import threading
import time
from typing import Callable, Optional
from utils.logger import logger

class AudioStreamManager:
    """
    Manages the microphone stream and provides chunks of audio data.
    """
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 4000, device_index: Optional[int] = None):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.audio_queue = queue.Queue()
        self._pyaudio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

    def _callback(self, in_data, frame_count, time_info, status):
        """Internal callback for PyAudio stream."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start(self):
        """Starts the audio capture in a background thread."""
        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Audio stream manager started")

    def stop(self):
        """Stops the audio capture."""
        self._is_running = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._thread:
            self._thread.join()
        logger.info("Audio stream manager stopped")

    def _run(self):
        """Continuously manages the audio stream with error recovery."""
        while self._is_running:
            try:
                self._stream = self._pyaudio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._callback
                )

                self._stream.start_stream()

                while self._is_running and self._stream.is_active():
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Microphone error: {e}. Restarting in 2 seconds...")
                if self._stream:
                    try:
                        self._stream.close()
                    except:
                        pass
                time.sleep(2)

    def get_audio_chunks(self):
        """Generator that yields audio chunks from the queue."""
        while self._is_running or not self.audio_queue.empty():
            try:
                yield self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

    def __del__(self):
        self._pyaudio.terminate()
