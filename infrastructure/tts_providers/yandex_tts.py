"""Yandex TTS provider implementation."""

import logging
import requests
from typing import Optional

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TtsProviderError
from infrastructure.tts_providers.base import BaseTtsProvider

logger = logging.getLogger(__name__)


class YandexTtsProvider(BaseTtsProvider):
    
    API_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    
    def __init__(self, api_key: str, folder_id: Optional[str] = None):
        if not api_key:
            raise ValueError("Yandex API key is required")
        
        self._api_key = api_key
        self._folder_id = folder_id
    
    def synthesize(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        try:
            headers = {
                "Authorization": f"Api-Key {self._api_key}"
            }
            
            data = {
                "text": text.content,
                "lang": config.language,
                "voice": config.voice,
                "speed": str(config.speed),
                "format": "oggopus"
            }
            
            if self._folder_id:
                data["folderId"] = self._folder_id
            
            if config.emotion:
                data["emotion"] = config.emotion
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code != 200:
                error_msg = f"Yandex TTS API error: {response.status_code}"
                try:
                    error_detail = response.json().get("message", "")
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                logger.error(error_msg)
                raise TtsProviderError(error_msg)
            
            audio_data = response.content
            
            return VoiceMessage(
                audio_data=audio_data,
                format="ogg",
                size=len(audio_data)
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Yandex TTS synthesis: {e}")
            raise TtsProviderError("Сервис временно недоступен. Попробуйте позже.") from e
        except TtsProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Yandex TTS synthesis: {e}", exc_info=True)
            raise TtsProviderError(f"Ошибка при генерации голоса: {e}") from e
