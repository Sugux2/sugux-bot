import asyncio
import os
import logging
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.__main__ import main

# Настройка логов, чтобы видеть ошибки в панели Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("highrise_bot")

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is alive!", 200

class MyBot(BaseBot):
    async def on_start(self, session_metadata) -> None:
        logger.info("Бот успешно зашел в сеть!")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        # Критически важно: два аргумента (user и position) для версии 24.1.0
        try:
            await self.highrise.chat(f"Привет, @{user.username}! Добро пожаловать!")
        except Exception as e:
            logger.error(f"Ошибка в on_user_join: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        # Реакция на цифры (эмоции)
        if message.isdigit():
            await self.highrise.send_emote(message, user.id)
        
        # Команда пинг
        if message.lower() == "!ping":
            await self.highrise.chat("Pong! Бот работает стабильно.")

def run_web():
    # Railway автоматически дает порт через переменную PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке, чтобы Railway не закрывал проект
    Thread(target=run_web, daemon=True).start()
    
    room_id = "69b56b7ebacc85f7998d47a9" # Твой ID комнаты
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        logger.error("ОШИБКА: API_KEY не найден в переменных окружения!")
    else:
        definitions = [("main:MyBot", room_id, api_key)]
        asyncio.run(main(definitions))
