# Telegram TTS Bot

Telegram-бот для преобразования текста в голосовые сообщения с использованием различных TTS провайдеров.

## Архитектура

Проект построен на основе Domain-Driven Design

## Возможности

- Преобразование текста в голосовые сообщения
- Поддержка нескольких TTS провайдеров:
  - Yandex Cloud TTS
  - Sber TTS (SaluteSpeech)
  - Open-source решения (gtts или pyttsx3)
- Автоматическая конвертация аудио в формат OGG/Opus для Telegram

## Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | Да |
| `TTS_PROVIDER` | Провайдер TTS: `YANDEX`, `SBER`, `OSS` | Да |
| `YANDEX_API_KEY` | API ключ Yandex Cloud | Если `TTS_PROVIDER=YANDEX` |
| `YANDEX_FOLDER_ID` | Folder ID Yandex Cloud | Нет |
| `SBER_API_KEY` | API ключ Sber | Если `TTS_PROVIDER=SBER` |
| `SBER_CLIENT_ID` | Client ID Sber | Нет |
| `FFMPEG_PATH` | Путь к ffmpeg | Нет |
| `WEBHOOK_URL` | URL для webhook | Нет |
| `WEBHOOK_PORT` | Порт для webhook | Нет |
| `LOG_LEVEL` | Уровень логирования | Нет |

## Использование

### Запуск бота

```bash
python bot.py
```
### Команды

- `/start` - Приветствие и краткая инструкция
- `/help` - Подробная справка по использованию

## Тестирование

Unittest:
```bash
python -m unittest discover tests
```
