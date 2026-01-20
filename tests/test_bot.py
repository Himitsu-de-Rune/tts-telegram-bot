"""Tests for Telegram bot."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import io

from domain.value_objects.text_message import TextMessage
from domain.value_objects.voice_message import VoiceMessage
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TextToSpeechService, TtsProviderError
from application.use_cases.generate_voice_message import GenerateVoiceMessageUseCase
from application.use_cases.handle_start_command import HandleStartCommandUseCase
from application.use_cases.handle_help_command import HandleHelpCommandUseCase


class TestTextMessage(unittest.TestCase):
    """Tests for TextMessage value object."""
    
    def test_valid_text_message(self):
        """Test creating valid text message."""
        text = TextMessage(content="Hello, world!")
        self.assertEqual(text.content, "Hello, world!")
        self.assertEqual(text.length, 13)
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with self.assertRaises(ValueError):
            TextMessage(content="")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        with self.assertRaises(ValueError):
            TextMessage(content="   ")
    
    def test_too_long_text_raises_error(self):
        """Test that text exceeding max length raises ValueError."""
        long_text = "a" * (TextMessage.MAX_LENGTH + 1)
        with self.assertRaises(ValueError):
            TextMessage(content=long_text)
    
    def test_max_length_text_is_valid(self):
        """Test that text at max length is valid."""
        text = TextMessage(content="a" * TextMessage.MAX_LENGTH)
        self.assertEqual(text.length, TextMessage.MAX_LENGTH)


class TestVoiceMessage(unittest.TestCase):
    """Tests for VoiceMessage value object."""
    
    def test_valid_voice_message(self):
        """Test creating valid voice message."""
        audio_data = b"fake_audio_data"
        voice = VoiceMessage(
            audio_data=audio_data,
            format="ogg",
            duration=5,
            size=len(audio_data)
        )
        self.assertEqual(voice.audio_data, audio_data)
        self.assertEqual(voice.format, "ogg")
        self.assertEqual(voice.size, len(audio_data))
    
    def test_empty_audio_raises_error(self):
        """Test that empty audio data raises ValueError."""
        with self.assertRaises(ValueError):
            VoiceMessage(audio_data=b"")
    
    def test_auto_size_calculation(self):
        """Test that size is auto-calculated if not provided."""
        audio_data = b"test_audio"
        voice = VoiceMessage(audio_data=audio_data)
        self.assertEqual(voice.size, len(audio_data))


class TestTtsConfig(unittest.TestCase):
    """Tests for TtsConfig value object."""
    
    def test_valid_config(self):
        """Test creating valid TTS config."""
        config = TtsConfig(
            voice="alena",
            language="ru-RU",
            speed=1.0
        )
        self.assertEqual(config.voice, "alena")
        self.assertEqual(config.speed, 1.0)
    
    def test_invalid_speed_raises_error(self):
        """Test that invalid speed raises ValueError."""
        with self.assertRaises(ValueError):
            TtsConfig(speed=-1)
        
        with self.assertRaises(ValueError):
            TtsConfig(speed=0)
        
        with self.assertRaises(ValueError):
            TtsConfig(speed=4.0)


class TestGenerateVoiceMessageUseCase(unittest.TestCase):
    """Tests for GenerateVoiceMessageUseCase."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_provider = Mock()
        self.mock_provider.synthesize = Mock(return_value=VoiceMessage(
            audio_data=b"test_audio",
            format="ogg"
        ))
        self.tts_service = TextToSpeechService(self.mock_provider)
        self.use_case = GenerateVoiceMessageUseCase(self.tts_service)
    
    def test_execute_success(self):
        """Test successful voice message generation."""
        result = self.use_case.execute("Hello, world!")
        
        self.assertIsInstance(result, VoiceMessage)
        self.mock_provider.synthesize.assert_called_once()
        call_args = self.mock_provider.synthesize.call_args
        self.assertIsInstance(call_args[0][0], TextMessage)
        self.assertIsInstance(call_args[0][1], TtsConfig)
    
    def test_execute_validation_error(self):
        """Test that validation errors are raised."""
        with self.assertRaises(ValueError):
            self.use_case.execute("")
    
    def test_execute_provider_error(self):
        """Test that provider errors are raised."""
        self.mock_provider.synthesize.side_effect = TtsProviderError("Provider error")
        
        with self.assertRaises(TtsProviderError):
            self.use_case.execute("Test text")


class TestHandleStartCommandUseCase(unittest.TestCase):
    """Tests for HandleStartCommandUseCase."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_case = HandleStartCommandUseCase()
    
    def test_execute_with_username(self):
        """Test start command with username."""
        result = self.use_case.execute(user_id=123, username="testuser")
        self.assertIn("testuser", result)
        self.assertIn("Привет", result)
    
    def test_execute_without_username(self):
        """Test start command without username."""
        result = self.use_case.execute(user_id=123)
        self.assertIn("пользователь", result)
        self.assertIn("Привет", result)


class TestHandleHelpCommandUseCase(unittest.TestCase):
    """Tests for HandleHelpCommandUseCase."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_case = HandleHelpCommandUseCase()
    
    def test_execute(self):
        """Test help command."""
        result = self.use_case.execute()
        self.assertIn("Справка", result)
        self.assertIn("2000", result)  # Max length mentioned


if __name__ == "__main__":
    unittest.main()
