import asyncio
import json
import os
import logging
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position
from highrise.__main__ import main

# Настройка логов для отслеживания ошибок в Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Flask сервер, чтобы Render видел активность на порту 10000
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот активен и работает!"

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.locs = {}
        if os.path.exists("locs.json"):
            try:
                with open("locs.json", "r") as f:
                    self.locs = json.load(f)
            except:
                self.locs = {}

    async def on_user_join(self, user: User, position: Position) -> None:
        await self.highrise.chat(f"Привет, @{user.username}! Напиши номер эмоции или 'тп [название]'.")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()

        # Команда для сохранения точки (только для админа/владельца)
        if msg.startswith("сейв "):
            name = msg.split(" ", 1)[1]
            room_users = await self.highrise.get_room_users()
            for u, p in room_users.content:
                if u.id == user.id and isinstance(p, Position):
                    self.locs[name] = [p.x, p.y, p.z, p.facing]
                    with open("locs.json", "w") as f:
                        json.dump(self.locs, f)
                    await self.highrise.chat(f"✅ Точка '{name}' сохранена!")

        # Команда для телепортации
        elif msg.startswith("тп "):
            loc = msg.split(" ", 1)[1]
            if loc in self.locs:
                p = self.locs[loc]
                await self.highrise.teleport(user.id, Position(p[0], p[1], p[2], p[3]))
            else:
                await self.highrise.chat(f"❌ Точка '{loc}' не найдена.")

        # Эмоции по цифрам
        elif msg.isdigit():
            await self.highrise.send_emote(msg, user.id)

def run_web():
    # Запуск на порту 10000, который требует Render
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # Запускаем веб-часть в отдельном потоке
    Thread(target=run_web, daemon=True).start()
    
    # Твой Room ID
    room_id = "69b56b7ebacc85f7998d47a9"
    
    # Берем токен из настроек Render
    api_key = os.environ.get("API_KEY")
    
    if api_key:
        # Важно: передаем definitions, чтобы не было ошибки TypeError
        definitions = [("main:MyBot", room_id, api_key)]
        logger.info("Запуск бота...")
        asyncio.run(main(definitions))
    else:
        logger.error("ОШИБКА: API_KEY не найден в Environment Variables!")
