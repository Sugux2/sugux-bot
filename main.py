import asyncio
import os
import logging
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata
import sys

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
        logger.info(f"✅ Bot started in room: {session_metadata.room_id}")
        await self.highrise.chat("Бот запущен!")

    # ИСПРАВЛЕНО: добавлен параметр position
    async def on_user_join(self, user: User, position: Position) -> None:
        logger.info(f"👤 User joined: {user.username}")
        await self.highrise.chat(f"Привет, @{user.username}")

    # ИСПРАВЛЕНО: правильные параметры
    async def on_chat(self, user: User, message: str) -> None:
        logger.info(f"💬 Chat from {user.username}: {message}")
        if message.isdigit():
            await self.highrise.send_emote(message, user.id)
    
    async def on_tip(self, sender: User, receiver: User, tip: int) -> None:
        logger.info(f"💰 Tip: {sender.username} tipped {receiver.username} {tip} gold")

    async def on_disconnect(self) -> None:
        logger.warning("⚠️ Bot disconnected!")

def run_flask():
    """Запуск Flask"""
    try:
        port = int(os.environ.get('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask error: {e}")

async def run_bot():
    """Запуск бота"""
    room_id = "69b56b7ebacc85f7998d47a9"
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        logger.error("❌ API_KEY not found!")
        return
    
    logger.info(f"🚀 Starting bot for room: {room_id}")
    
    # Правильный запуск бота
    bot_instance = MyBot()
    await bot_instance.start(room_id, api_key)

def main():
    """Главная функция"""
    logger.info("Starting application...")
    
    # Запускаем Flask
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask server started")
    
    # Запускаем бота
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()