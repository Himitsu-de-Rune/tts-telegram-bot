"""Use case for handling /start command."""

from typing import Optional


class HandleStartCommandUseCase:
    
    def execute(self, user_id: int, username: Optional[str] = None) -> str:
        name = username or "пользователь"
        return (
            f"Привет, {name}! 👋\n\n"
            "Я бот для преобразования текста в голосовые сообщения.\n\n"
            "Просто отправь мне текстовое сообщение, и я озвучу его для тебя!\n\n"
            "Используй /help для получения дополнительной информации."
        )
