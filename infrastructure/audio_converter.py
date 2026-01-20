"""Audio converter for converting audio formats to OGG/Opus."""

import logging
import subprocess
import tempfile
import os
from pathlib import Path

from domain.value_objects.voice_message import VoiceMessage
from domain.services.text_to_speech_service import TtsProviderError

logger = logging.getLogger(__name__)


class AudioConverter:
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self._ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is available."""
        try:
            subprocess.run(
                [self._ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                check=True
            )
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(
                f"ffmpeg not found at {self._ffmpeg_path}. "
                "Audio conversion may fail. Install ffmpeg or set FFMPEG_PATH environment variable."
            )
    
    def convert_to_ogg_opus(self, voice_message: VoiceMessage) -> VoiceMessage:
        # If already in OGG format, return as is
        if voice_message.format.lower() in ['ogg', 'opus']:
            return voice_message
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{voice_message.format}"
            ) as input_file:
                input_file.write(voice_message.audio_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".ogg"
            ) as output_file:
                output_path = output_file.name
            
            try:
                # Convert using ffmpeg
                cmd = [
                    self._ffmpeg_path,
                    "-i", input_path,
                    "-acodec", "libopus",
                    "-f", "ogg",
                    "-y",  # Overwrite output file
                    output_path
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    check=True
                )
                
                # Read converted audio
                with open(output_path, 'rb') as f:
                    converted_data = f.read()
                
                return VoiceMessage(
                    audio_data=converted_data,
                    format="ogg",
                    size=len(converted_data)
                )
                
            finally:
                # Cleanup temp files
                try:
                    os.unlink(input_path)
                except:
                    pass
                try:
                    os.unlink(output_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg conversion timeout")
            raise TtsProviderError("Превышено время ожидания конвертации аудио")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg conversion error: {e.stderr.decode() if e.stderr else str(e)}")
            raise TtsProviderError("Ошибка конвертации аудио")
        except Exception as e:
            logger.error(f"Unexpected error during audio conversion: {e}", exc_info=True)
            raise TtsProviderError(f"Ошибка конвертации аудио: {e}") from e
