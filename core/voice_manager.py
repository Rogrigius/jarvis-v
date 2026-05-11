"""
Voice management system for JARVIS, handling TTS and STT.
"""
import asyncio
import edge_tts
import pygame
import os
import tempfile
from typing import Optional
from utils.logger import logger
from models.event import Event, EventType

class VoiceManager:
    """
    Manages speech synthesis (TTS) and voice recognition (STT).
    Uses Edge-TTS for high-quality voice synthesis.
    """
    def __init__(self, event_bus, voice_name: str = "en-US-GuyNeural"):
        self.event_bus = event_bus
        self.voice_name = voice_name
        pygame.mixer.init()

    async def speak(self, text: str):
        """
        Convert text to speech and play it.

        Args:
            text: The text string to speak.
        """
        logger.info(f"Speaking: {text}")
        await self.event_bus.emit(Event(EventType.VOICE_START, {"text": text}, "VoiceManager"))

        tmp_path = None
        try:
            communicate = edge_tts.Communicate(text, self.voice_name)

            # Use a temporary file to store the speech audio
            # We close it immediately so pygame can open it later without file locking issues
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_path = tmp_file.name

            # Save the TTS output to the file
            await communicate.save(tmp_path)

            # Play the audio using pygame
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            pygame.mixer.music.unload()

            # Clean up the temporary file after playback
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {tmp_path}: {e}")

        except Exception as e:
            logger.error(f"TTS Error: {e}")

        await self.event_bus.emit(Event(EventType.VOICE_END, {"text": text}, "VoiceManager"))

    async def start_listening(self):
        """
        Placeholder for Speech-to-Text (STT) logic.
        In a full implementation, this would use Vosk or Whisper to listen
        continuously and emit COMMAND_DETECTED events.
        """
        logger.info("Voice listening started (STT placeholder)")
        # Implementation would involve opening an audio stream and passing data to Vosk/Whisper
        pass
