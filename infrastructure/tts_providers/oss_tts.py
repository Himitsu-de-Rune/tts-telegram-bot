"""Open-source TTS provider implementation using gTTS or pyttsx3."""

import logging
import io
import tempfile
import os
from typing import Optional

try:
    from gtts import gTTS  # pyright: ignore[reportMissingImports]
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3  # pyright: ignore[reportMissingImports]
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TtsProviderError
from infrastructure.tts_providers.base import BaseTtsProvider

logger = logging.getLogger(__name__)


class OssTtsProvider(BaseTtsProvider):
    
    def __init__(self, prefer_gtts: bool = True):
        if prefer_gtts and not GTTS_AVAILABLE:
            if PYTTSX3_AVAILABLE:
                logger.warning("gTTS not available, falling back to pyttsx3")
                prefer_gtts = False
            else:
                raise ImportError(
                    "Neither gTTS nor pyttsx3 is available. "
                    "Install gtts: pip install gtts or pyttsx3: pip install pyttsx3"
                )
        
        self._prefer_gtts = prefer_gtts and GTTS_AVAILABLE
    
    def synthesize(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        try:
            if self._prefer_gtts:
                return self._synthesize_gtts(text, config)
            elif PYTTSX3_AVAILABLE:
                return self._synthesize_pyttsx3(text, config)
            else:
                raise TtsProviderError("No TTS library available")
                
        except TtsProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during OSS TTS synthesis: {e}", exc_info=True)
            raise TtsProviderError(f"Ошибка при генерации голоса: {e}") from e
    
    def _synthesize_gtts(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        try:
            lang_map = {
                "ru-RU": "ru",
                "en-US": "en",
                "en-GB": "en"
            }
            lang = lang_map.get(config.language, config.language.split("-")[0])
            
            tts = gTTS(text=text.content, lang=lang, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_data = audio_buffer.getvalue()
            
            return VoiceMessage(
                audio_data=audio_data,
                format="mp3",  # gTTS outputs MP3
                size=len(audio_data)
            )
            
        except Exception as e:
            logger.error(f"gTTS synthesis error: {e}")
            raise TtsProviderError(f"Ошибка gTTS: {e}") from e
    
    def _synthesize_pyttsx3(self, text: TextMessage, config: TtsConfig) -> VoiceMessage:
        temp_path = None
        try:
            engine = pyttsx3.init()
            
            # Set voice properties
            engine.setProperty('rate', int(200 * config.speed))
            
            # Try to set voice by language
            voices = engine.getProperty('voices')
            if voices:
                if config.language.startswith("ru"):
                    for voice in voices:
                        if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            break
            
            # Create temporary file for pyttsx3 (it requires a file path)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Save to temporary file
            engine.save_to_file(text.content, temp_path)
            engine.runAndWait()
            
            # Read the generated audio file
            try:
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
            except FileNotFoundError:
                raise TtsProviderError("Failed to generate audio file")
            
            return VoiceMessage(
                audio_data=audio_data,
                format="wav",
                size=len(audio_data)
            )
            
        except Exception as e:
            logger.error(f"pyttsx3 synthesis error: {e}")
            raise TtsProviderError(f"Ошибка pyttsx3: {e}") from e
        finally:
            # Cleanup temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
