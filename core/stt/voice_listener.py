"""
Voice listening manager that orchestrates audio capture, STT, and wake-word detection.
"""
import asyncio
import threading
from core.stt.audio_stream_manager import AudioStreamManager
from core.stt.speech_recognizer import SpeechRecognizer
from core.stt.wake_word_detector import WakeWordDetector
from models.event import Event, EventType
from utils.logger import logger

class VoiceListener:
    """
    Main entry point for voice interaction.
    Runs in a background thread and emits events to the EventBus.
    """
    def __init__(self, event_bus, config):
        self.event_bus = event_bus
        self.config = config

        self.audio_manager = AudioStreamManager(
            sample_rate=config.stt_sample_rate,
            chunk_size=config.stt_chunk_size
        )
        self.recognizer = SpeechRecognizer(
            model_path=config.stt_model_path,
            sample_rate=config.stt_sample_rate
        )
        self.wake_detector = WakeWordDetector(
            wake_words=config.stt_wake_words
        )

        self._is_active = False
        self._loop = None

    def start(self):
        """Starts the voice listening process."""
        self._is_active = True
        self.audio_manager.start()

        # Start the processing loop in a separate thread
        thread = threading.Thread(target=self._processing_loop, daemon=True)
        thread.start()
        logger.info("VoiceListener processing loop started")

    def stop(self):
        """Stops the voice listening process."""
        self._is_active = False
        self.audio_manager.stop()

    def _processing_loop(self):
        """Continuously processes audio chunks and detects speech/wake-words."""
        # Create a new event loop for this thread to handle async emitting
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        for chunk in self.audio_manager.get_audio_chunks():
            if not self._is_active:
                break

            text = self.recognizer.process_chunk(chunk)
            if text:
                logger.debug(f"Recognized: {text}")

                if self.wake_detector.check(text):
                    clean_text = self.wake_detector.strip_wake_word(text)

                    # If there's content after the wake word, treat it as a command
                    if clean_text:
                        self._emit_command(clean_text)
                    else:
                        # Just the wake word, maybe JARVIS should say "Yes?"
                        self._emit_event(EventType.COMMAND_DETECTED, {"text": text})
                else:
                    # Not a wake word, but we might still want to show it in the UI
                    # or handle context-aware follow-up commands
                    self._emit_event(EventType.COMMAND_DETECTED, {"text": text})

            # Partial results for UI feedback
            partial = self.recognizer.get_partial()
            if partial:
                # We could emit a PARTIAL_RECOGNITION event here
                pass

    def _emit_command(self, text: str):
        """Emits a command event to the event bus."""
        self._emit_event(EventType.COMMAND_DETECTED, {"text": text})

    def _emit_event(self, event_type: EventType, data: dict):
        """Helper to emit events asynchronously from the processing thread."""
        if self._loop:
            future = asyncio.run_coroutine_threadsafe(
                self.event_bus.emit(Event(event_type, data, "VoiceListener")),
                self._loop
            )
            # We don't necessarily wait for the result to keep the loop fast
