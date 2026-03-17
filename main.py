import asyncio, json, os
from threading import Thread
from flask import Flask
from highrise import BaseBot, User
from highrise.models import SessionMetadata, Position
from highrise.__main__ import main

# Веб-сервер
app = Flask(__name__)
@app.route('/')
def index(): return "Sugux Bot is Working!"

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
        await self.highrise.chat(f"Привет, @{user.username}! Добро пожаловать! 👋")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()
        privs = await self.highrise.get_bundle_privileges(user.id)
        is_admin = privs.content.get("is_owner", False) or privs.content.get("is_moderator", False)
        is_vip = str(user.id) in self.vips or is_admin

        if msg.startswith("сейв ") and is_admin:
            name = msg.split(" ", 1)[1]
            room_users = await self.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.id == user.id and isinstance(pos, Position):
                    self.locs[name] = [pos.x, pos.y, pos.z, pos.facing]
                    with open("locs.json", "w") as f: json.dump(self.locs, f)
                    await self.highrise.chat(f"✅ Точка '{name}' сохранена!")

        elif msg.startswith("удалить ") and is_admin:
            name = msg.split(" ", 1)[1]
            if name in self.locs:
                del self.locs[name]
                with open("locs.json", "w") as f: json.dump(self.locs, f)
                await self.highrise.chat(f"🗑 Точка '{name}' удалена.")

        elif msg.startswith("вип дай ") and is_admin:
            try:
                target_name = msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, p in room_users.content:
                    if u.username.lower() == target_name:
                        if str(u.id) not in self.vips:
                            self.vips.append(str(u.id))
                            with open("vips.json", "w") as f: json.dump(self.vips, f)
                            await self.highrise.chat(f"🌟 @{u.username} теперь VIP!")
                        break
            except: pass

        elif msg.startswith("тп ") or msg == "вип":
            target_loc = "вип" if msg == "вип" else msg.split(" ", 1)[1]
            if target_loc in self.locs:
                if target_loc == "вип" and not is_vip:
                    await self.highrise.chat("🔒 Доступ только для VIP.")
                else:
                    l = self.locs[target_loc]
                    await self.highrise.teleport(user.id, Position(l[0], l[1], l[2], l[3]))
            else:
                await self.highrise.chat(f"❓ Точка '{target_loc}' не найдена.")

        elif msg.isdigit():
            await self.highrise.send_emote(msg, user.id)

def run_web():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run_web).start()
    # Запуск бота
    room_id = "6300a02c6c0f7d15f7a783b6"
    api_key = os.environ.get("API_KEY")
    if api_key:
        definitions = [("main:MyBot", room_id, api_key)]
        asyncio.run(main(definitions))
    else:
        print("ОШИБКА: API_KEY не найден в настройках Render!")
