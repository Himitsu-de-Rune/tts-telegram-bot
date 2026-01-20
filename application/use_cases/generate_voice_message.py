"""Use case for generating voice message from text."""

import logging
from typing import Optional

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TextToSpeechService, TtsProviderError

logger = logging.getLogger(__name__)


class GenerateVoiceMessageUseCase:
    
    def __init__(self, tts_service: TextToSpeechService):
        self._tts_service = tts_service
    
    def execute(
        self,
        text: str,
        user_id: Optional[int] = None,
        config: Optional[TtsConfig] = None
    ) -> VoiceMessage:
        try:
            # Create domain objects
            text_message = TextMessage(content=text)
            tts_config = config or TtsConfig()
            
            # Synthesize speech
            voice_message = self._tts_service.synthesize(text_message, tts_config)
            
            logger.info(
                f"Successfully generated voice message for user {user_id}. "
                f"Text length: {text_message.length}, Audio size: {voice_message.size} bytes"
            )
            
            return voice_message
            
        except ValueError as e:
            logger.warning(f"Validation error for user {user_id}: {e}")
            raise
        except TtsProviderError as e:
            logger.error(f"TTS provider error for user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for user {user_id}: {e}", exc_info=True)
            raise TtsProviderError(f"Failed to generate voice message: {e}") from e
