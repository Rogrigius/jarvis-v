"""
Speech-to-Text implementation using Vosk.
"""
import json
import os
from vosk import Model, KaldiRecognizer
from utils.logger import logger

class SpeechRecognizer:
    """
    Handles transcription of audio chunks into text using the Vosk engine.
    """
    def __init__(self, model_path: str, sample_rate: int = 16000):
        if not os.path.exists(model_path):
            logger.error(f"Vosk model not found at {model_path}. Please download it.")
            # We don't raise an exception here to allow the system to boot
            # even if STT is unavailable (will log errors later).
            self.model = None
            self.recognizer = None
        else:
            logger.info(f"Loading Vosk model from {model_path}...")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, sample_rate)
            logger.info("Vosk model loaded successfully")

    def process_chunk(self, chunk: bytes) -> str:
        """
        Processes a single chunk of audio data.

        Returns:
            Transcribed text if a complete phrase is detected, else empty string.
        """
        if not self.recognizer:
            return ""

        if self.recognizer.AcceptWaveform(chunk):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "")
        return ""

    def get_partial(self) -> str:
        """Returns the current partial transcription."""
        if not self.recognizer:
            return ""
        result = json.loads(self.recognizer.PartialResult())
        return result.get("partial", "")
