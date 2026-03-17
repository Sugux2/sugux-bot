import asyncio
import time
from highrise import BaseBot, User, Position
from emotes_data import EMOTES_LIST
from flask import Flask
from threading import Thread

# --- ВЕБ-СЕРВЕР ДЛЯ 24/7 ---
app = Flask('')
@app.route('/')
def home(): return "Sugux Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# --- ЛОГИКА БОТА ---
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_join_times = {}
        self.locations = {}
        self.vips = []
        self.owner_id = None

    async def on_start(self, session_metadata):
        self.owner_id = session_metadata.user_id
        print(f"Бот онлайн! ID владельца: {self.owner_id}")

    async def on_user_join(self, user: User, position):
        self.user_join_times[user.id] = time.time()
        await self.highrise.chat(f"@{user.username}, твой вайб идеально вписывается! Оставайся с нами. ✨")

    async def on_chat(self, user: User, message: str) -> None:
        m = message.lower().strip()
        uid = user.id
        uname = user.username

        # 1. МГНОВЕННЫЕ АНИМАЦИИ (1-218)
        if m in EMOTES_LIST:
            asyncio.create_task(self.highrise.send_emote(EMOTES_LIST[m], uid))
            return

        # 2. СТАТИСТИКА (ШЕПОТОМ)
        if m == "стата":
            start_time = self.user_join_times.get(uid, time.time())
            minutes = int((time.time() - start_time) // 60)
            await self.highrise.send_whisper(uid, f"Твой актив: {minutes} мин. 🔥")
            return

        # 3. ХЕЛП (ШЕПОТОМ)
        if m in ["хелп", "помощь"]:
            help_text = "🕺 Анимации 1-218 | 📍 Локации: пиши название | 📊 стата — твой актив."
            await self.highrise.send_whisper(uid, help_text)
            return

        # 4. КОМАНДЫ ВЛАДЕЛЬЦА (АВТО-АДМИН)
        if uid == self.owner_id:
            if m.startswith("!save "):
                loc_name = m[6:].strip()
                # Получаем текущую позицию владельца
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == uid:
                        self.locations[loc_name] = pos
                        await self.highrise.send_whisper(uid, f"Локация '{loc_name}' сохранена!")
                return

            if m.startswith("!vip "):
                target = m.split("@")[-1].strip()
                if target not in self.vips:
                    self.vips.append(target)
                    await self.highrise.send_whisper(uid, f"@{target} теперь VIP!")
                return

        # 5. ТЕЛЕПОРТЫ ПО ЛОКАЦИЯМ
        if m in self.locations:
            await self.highrise.teleport(uid, self.locations[m])
            return

        # 6. VIP ТЕЛЕПОРТ К ИГРОКУ (ДЛЯ АДМИНА И VIP)
        if m.startswith("тп к ") and (uid == self.owner_id or uname in self.vips):
            target_name = m.split("@")[-1].strip().lower()
            room_users = await self.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.username.lower() == target_name:
                    await self.highrise.teleport(uid, pos)
                    break

    async def on_user_leave(self, user: User):
        if user.id in self.user_join_times:
            del self.user_join_times[user.id]

# --- ЗАПУСК ---
if __name__ == "__main__":
    # Запускаем сайт в отдельном потоке
    Thread(target=run_web).start()
    
    # Запускаем бота (убедись, что токен и ID комнаты вставлены в настройки хостинга)
    from highrise.__main__ import main
    # Для Render лучше использовать переменные окружения, но можно и напрямую в main()
    # main() подтянет данные из командной строки или настроек
