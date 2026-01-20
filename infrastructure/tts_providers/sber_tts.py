"""Sber TTS provider implementation."""

import logging
import uuid
import requests
from typing import Optional

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TtsProviderError
from infrastructure.tts_providers.base import BaseTtsProvider

logger = logging.getLogger(__name__)


class SberTtsProvider(BaseTtsProvider):
    
    API_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
    
    def __init__(self, api_key: str, client_id: Optional[str] = None):
        if not api_key:
            raise ValueError("Sber API key is required")
        
        self._api_key = api_key
        self._client_id = client_id
        self._access_token = self.get_access_token()
    
    def synthesize(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/text",
            }
            
            if self._client_id:
                headers["X-Client-Id"] = self._client_id
            
            params = {
                "lang": config.language,
                "voice": "Pon_24000",
                "speed": str(config.speed),
                "format": "opus"
            }
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                params=params,
                data=text.content,
                timeout=10,
                verify=False
            )
            
            if response.status_code != 200:
                error_msg = f"Sber TTS API error: {response.status_code}"
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", "") or error_json.get("message", "")
                    if error_detail:
                        error_msg += f" - {error_detail}"
                        if error_detail == "Token has expired":
                            self._access_token = self.get_access_token()
                            error_msg += f" - New access token received"
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
            logger.error(f"Network error during Sber TTS synthesis: {e}")
            raise TtsProviderError("Сервис временно недоступен. Попробуйте позже.") from e
        except TtsProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Sber TTS synthesis: {e}", exc_info=True)
            raise TtsProviderError(f"Ошибка при генерации голоса: {e}") from e

    def get_access_token(self):

        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        data={
          'scope': 'SALUTE_SPEECH_PERS'
        }
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
          'RqUID': str(uuid.uuid4()),
          'Authorization': f'Basic {self._api_key}'
        }

        response = requests.request("POST", url, headers=headers, data=data, verify=False)
        return response.json()["access_token"]
