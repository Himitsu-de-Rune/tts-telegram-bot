"""Telegram bot main entry point."""

import logging
import sys
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import Config
from domain.value_objects.tts_config import TtsConfig
from domain.services.text_to_speech_service import TextToSpeechService, TtsProviderError
from application.use_cases.generate_voice_message import GenerateVoiceMessageUseCase
from application.use_cases.handle_start_command import HandleStartCommandUseCase
from application.use_cases.handle_help_command import HandleHelpCommandUseCase
from infrastructure.tts_providers.yandex_tts import YandexTtsProvider
from infrastructure.tts_providers.sber_tts import SberTtsProvider
from infrastructure.tts_providers.oss_tts import OssTtsProvider
from infrastructure.audio_converter import AudioConverter


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper())
)
logger = logging.getLogger(__name__)


def create_tts_provider():
    """Create TTS provider based on configuration."""
    provider_name = Config.TTS_PROVIDER
    provider_config = Config.get_tts_provider_config()
    
    if provider_name == "YANDEX":
        return YandexTtsProvider(**provider_config)
    elif provider_name == "SBER":
        return SberTtsProvider(**provider_config)
    elif provider_name == "OSS":
        return OssTtsProvider(**provider_config)
    else:
        raise ValueError(f"Unknown TTS provider: {provider_name}")


def create_application() -> Application:
    """Create and configure Telegram bot application."""
    # Validate configuration
    Config.validate()
    
    # Create TTS provider
    tts_provider = create_tts_provider()
    tts_service = TextToSpeechService(tts_provider)
    
    # Create audio converter
    audio_converter = AudioConverter(ffmpeg_path=Config.FFMPEG_PATH)
    
    # Create use cases
    generate_voice_use_case = GenerateVoiceMessageUseCase(tts_service)
    start_command_use_case = HandleStartCommandUseCase()
    help_command_use_case = HandleHelpCommandUseCase()
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", lambda u, c: handle_start(u, c, start_command_use_case)))
    application.add_handler(CommandHandler("help", lambda u, c: handle_help(u, c, help_command_use_case)))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda u, c: handle_text_message(u, c, generate_voice_use_case, audio_converter)
        )
    )
    application.add_handler(
        MessageHandler(
            filters.ALL,
            handle_unsupported_message
        )
    )
    
    return application


async def handle_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_case: HandleStartCommandUseCase
):
    """Handle /start command."""
    user = update.effective_user
    message = use_case.execute(
        user_id=user.id if user else 0,
        username=user.username if user else None
    )
    await update.message.reply_text(message)


async def handle_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_case: HandleHelpCommandUseCase
):
    """Handle /help command."""
    message = use_case.execute()
    await update.message.reply_text(message, parse_mode="Markdown")


async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_case: GenerateVoiceMessageUseCase,
    audio_converter: AudioConverter
):
    """Handle text message and generate voice."""
    user = update.effective_user
    user_id = user.id if user else 0
    text = update.message.text

    if not text:
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение.")
        return
    
    try:
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="record_voice"
        )
        
        # Generate voice message
        voice_message = use_case.execute(text=text, user_id=user_id)
        
        # Convert to OGG/Opus if needed
        if voice_message.format.lower() not in ['ogg', 'opus']:
            voice_message = audio_converter.convert_to_ogg_opus(voice_message)
        
        # Send voice message
        await update.message.reply_voice(
            voice=voice_message.audio_data,
            filename="voice.ogg"
        )
        
    except ValueError as e:
        error_message = str(e)
        if "exceeds maximum length" in error_message:
            await update.message.reply_text(
                f"Текст слишком длинный. Максимальная длина: {2000} символов."
            )
        elif "cannot be empty" in error_message:
            await update.message.reply_text("Текст не может быть пустым.")
        else:
            await update.message.reply_text(f"Ошибка валидации: {error_message}")
        
    except TtsProviderError as e:
        error_message = str(e)
        if "недоступен" in error_message.lower() or "unavailable" in error_message.lower():
            await update.message.reply_text("Сервис временно недоступен. Попробуйте позже.")
        else:
            await update.message.reply_text(f"Ошибка при генерации голоса: {error_message}")
        
    except Exception as e:
        logger.error(f"Unexpected error handling text message for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text("Произошла непредвиденная ошибка. Попробуйте позже.")


async def handle_unsupported_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Handle unsupported message types."""
    await update.message.reply_text(
        "Отправьте текстовое сообщение, я озвучу его для вас."
    )


def main():
    """Main entry point."""
    try:
        application = create_application()
        
        # Setup webhook if configured, otherwise use polling
        if Config.WEBHOOK_URL:
            logger.info(f"Starting bot with webhook: {Config.WEBHOOK_URL}")
            application.run_webhook(
                listen="0.0.0.0",
                port=Config.WEBHOOK_PORT,
                webhook_url=Config.WEBHOOK_URL
            )
        else:
            logger.info("Starting bot with polling")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
