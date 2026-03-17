import asyncio, json, os
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position
from highrise.models import SessionMetadata

app = Flask(__name__)
@app.route('/')
def index(): return "Sugux Bot is Running!"

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.loc_file = "locs.json"
        self.vips_file = "vips.json"
        self.locs = self.load_data(self.loc_file)
        self.vips = self.load_data(self.vips_file)

    def load_data(self, file):
        if os.path.exists(file):
            with open(file, "r") as f: return json.load(f)
        return {}

    def save_data(self, data, file):
        with open(file, "w") as f: json.dump(data, f)

    async def on_user_join(self, user: User, position: Position) -> None:
        # Авто-приветствие при входе игрока
        await self.highrise.chat(f"Привет, @{user.username}! Добро пожаловать! 👋")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()
        user_id = user.id
        
        # Проверка прав (Владелец или Модератор комнаты = Админ)
        permissions = await self.highrise.get_bundle_privileges(user_id)
        is_admin = permissions.content.get("is_moderator", False) or permissions.content.get("is_owner", False)
        is_vip = str(user_id) in self.vips or is_admin

        # 1. СОХРАНЕНИЕ (Админ) — "сейв название"
        if msg.startswith("сейв ") and is_admin:
            name = msg.split(" ", 1)[1]
            room_users = await self.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.id == user.id and isinstance(pos, Position):
                    self.locs[name] = [pos.x, pos.y, pos.z, pos.facing]
                    self.save_data(self.locs, self.loc_file)
                    await self.highrise.chat(f"✅ Точка '{name}' сохранена!")

        # 2. УДАЛЕНИЕ (Админ) — "удалить название"
        elif msg.startswith("удалить ") and is_admin:
            name = msg.split(" ", 1)[1]
            if name in self.locs:
                del self.locs[name]
                self.save_data(self.locs, self.loc_file)
                await self.highrise.chat(f"🗑 Точка '{name}' удалена.")

        # 3. ВЫДАЧА VIP (Админ) — "вип дай @ник"
        elif msg.startswith("вип дай ") and is_admin:
            try:
                username = msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                target_id = next((u.id for u, p in room_users.content if u.username.lower() == username), None)
                if target_id:
                    self.vips[str(target_id)] = username
                    self.save_data(self.vips, self.vips_file)
                    await self.highrise.chat(f"🌟 @{username} теперь VIP!")
                else: await self.highrise.chat("Игрок не найден в комнате.")
            except: await self.highrise.chat("Пример: вип дай @ник")

        # 4. ТЕЛЕПОРТ — "тп название" или просто "вип"
        elif msg.startswith("тп ") or msg == "вип":
            loc_name = "вип" if msg == "вип" else msg.split(" ", 1)[1]
            if loc_name in self.locs:
                if loc_name == "вип" and not is_vip:
                    await self.highrise.chat("🔒 Только для VIP!")
                else:
                    p = self.locs[loc_name]
                    await self.highrise.teleport(user_id, Position(p[0], p[1], p[2], p[3]))
            else: await self.highrise.chat(f"❓ Точка '{loc_name}' не найдена.")

        # 5. АНИМАЦИИ
        elif msg.isdigit():
            await self.highrise.send_emote(msg, user_id)

def run_web():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run_web).start()
    from highrise.__main__ import main
    os.environ["ROOM_ID"] = "6300a02c6c0f7d15f7a783b6"
    main()
