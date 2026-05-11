"""
Wake-word detection logic for JARVIS.
"""
from typing import List
from utils.logger import logger

class WakeWordDetector:
    """
    Monitors transcribed text for specific wake words.
    """
    def __init__(self, wake_words: List[str]):
        self.wake_words = [w.lower() for w in wake_words]
        logger.info(f"Wake-word detector initialized with: {self.wake_words}")

    def check(self, text: str) -> bool:
        """
        Checks if any wake word is present in the text.

        Args:
            text: Transcribed speech text.

        Returns:
            True if wake word detected, False otherwise.
        """
        if not text:
            return False

        text = text.lower()
        for word in self.wake_words:
            if word in text:
                logger.info(f"Wake-word detected: {word}")
                return True
        return False

    def strip_wake_word(self, text: str) -> str:
        """
        Removes the wake word from the start or end of the text.
        """
        text = text.lower()
        for word in self.wake_words:
            if word in text:
                # Basic removal, could be improved with regex
                text = text.replace(word, "").strip()
        return text
