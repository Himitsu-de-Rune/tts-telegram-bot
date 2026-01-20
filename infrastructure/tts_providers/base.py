"""Base TTS provider interface."""

from abc import ABC, abstractmethod

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TtsProviderError


class BaseTtsProvider(ABC):
    
    @abstractmethod
    def synthesize(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        """
        Synthesize speech from text.
        
        Args:
            text: Text message to synthesize
            config: TTS configuration
            
        Returns:
            Voice message with audio data
            
        Raises:
            TtsProviderError: If synthesis fails
        """
        pass
