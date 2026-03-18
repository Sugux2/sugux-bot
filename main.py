import os
import logging
from highrise import BaseBot, User, Position
from highrise.__main__ import main
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyBot(BaseBot):
    async def on_start(self, session_metadata) -> None:
        logger.info("✅ Бот успешно запущен!")
        await self.highrise.chat("Бот онлайн!")

    async def on_user_join(self, user: User, position: Position) -> None:
        logger.info(f"👤 Пользователь зашел: {user.username}")
        await self.highrise.chat(f"Привет, {user.username}!")

    async def on_chat(self, user: User, message: str) -> None:
        logger.info(f"💬 {user.username}: {message}")

if __name__ == "__main__":
    room_id = "69b56b7ebacc85f7998d47a9"
    api_key = os.environ.get("API_KEY")
    
    if not api_key:
        logger.error("❌ API_KEY не найден!")
        exit(1)
    
    logger.info(f"🚀 Запуск бота в комнате {room_id}")
    
    # Правильный запуск для SDK 24.1.0
    definitions = [("main:MyBot", room_id, api_key)]
    asyncio.run(main(definitions))