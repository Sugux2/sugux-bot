import asyncio, json, os, logging
from threading import Thread
from flask import Flask
from highrise import BaseBot, User
from highrise.models import SessionMetadata, Position
from highrise.__main__ import main

# Логирование, чтобы видеть ошибки в консоли Render
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def index(): return "Bot is Online!"

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.locs = {}
        self.vips = []
        if os.path.exists("locs.json"):
            with open("locs.json", "r") as f: self.locs = json.load(f)
        if os.path.exists("vips.json"):
            with open("vips.json", "r") as f: self.vips = json.load(f)

    async def on_user_join(self, user: User, position: Position) -> None:
        await self.highrise.chat(f"Привет, @{user.username}! 👋")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()
        privs = await self.highrise.get_bundle_privileges(user.id)
        is_admin = privs.content.get("is_owner", False) or privs.content.get("is_moderator", False)
        
        # Админ-команды: сейв, удалить, вип дай
        if msg.startswith("сейв ") and is_admin:
            name = msg.split(" ", 1)[1]
            room_users = await self.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.id == user.id and isinstance(pos, Position):
                    self.locs[name] = [pos.x, pos.y, pos.z, pos.facing]
                    with open("locs.json", "w") as f: json.dump(self.locs, f)
                    await self.highrise.chat(f"✅ Точка '{name}' сохранена!")

        elif msg.startswith("тп ") or msg == "вип":
            target = "вип" if msg == "вип" else msg.split(" ", 1)[1]
            if target in self.locs:
                l = self.locs[target]
                await self.highrise.teleport(user.id, Position(l[0], l[1], l[2], l[3]))

        elif msg.isdigit():
            await self.highrise.send_emote(msg, user.id)

def run_web():
    # Render дает порт 10000 для веб-сервера
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    Thread(target=run_web, daemon=True).start()
    
    # Запуск бота Highrise
    room_id = "6300a02c6c0f7d15f7a783b6"
    api_key = os.environ.get("API_KEY") # Берем из настроек Render
    
    if not api_key:
        print("ОШИБКА: API_KEY не найден в Environment Variables!")
    else:
        # Новый формат запуска для свежих версий SDK
        definitions = [("main:MyBot", room_id, api_key)]
        asyncio.run(main(definitions))
