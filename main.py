import asyncio
import os
import logging
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata
from highrise.__main__ import main as bot_main
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index(): 
    return "Bot is running"

@app.route('/health')
def health():
    return "OK", 200

class MyBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        logger.info(f"Bot started in room: {session_metadata.room_id}")
        await self.highrise.chat("Бот запущен и готов к работе!")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        logger.info(f"User joined: {user.username}")
        await self.highrise.chat(f"Привет, @{user.username}")

    async def on_chat(self, user: User, message: str) -> None:
        logger.info(f"Chat from {user.username}: {message}")
        if message.isdigit():
            await self.highrise.send_emote(message, user.id)

    async def on_disconnect(self) -> None:
        logger.warning("Bot disconnected!")
        # Можно добавить логику переподключения

def run_flask():
    """Запуск Flask сервера в отдельном потоке"""
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

async def run_bot():
    """Запуск бота Highrise"""
    room_id = "69b56b7ebacc85f7998d47a9"
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        logger.error("API_KEY not found in environment variables!")
        return
    
    try:
        logger.info(f"Starting bot for room: {room_id}")
        # Формируем аргументы командной строки для бота
        sys.argv = ["python", "main:MyBot", room_id, api_key]
        
        # Запускаем бота
        await bot_main([("main:MyBot", room_id, api_key)])
    except Exception as e:
        logger.error(f"Bot error: {e}")

def main():
    """Основная функция"""
    logger.info("Starting application...")
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started")
    
    # Запускаем бота в основном потоке
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()