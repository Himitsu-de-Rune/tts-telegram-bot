"""Domain service for text-to-speech operations."""

from abc import ABC, abstractmethod
from typing import Protocol

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig


class TtsProvider(Protocol):
    """Protocol for TTS provider implementations."""
    
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


class TtsProviderError(Exception):
    """Base exception for TTS provider errors."""
    pass


class TextToSpeechService:
    """Domain service for text-to-speech operations."""
    
    def __init__(self, provider: TtsProvider):
        self._provider = provider
    
    def synthesize(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        return self._provider.synthesize(text, config)
