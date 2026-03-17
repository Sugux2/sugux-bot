import asyncio, json, os
from threading import Thread
from flask import Flask
from highrise import BaseBot, User, Position
from highrise.__main__ import main

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive!"

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.locs = {}
        if os.path.exists("locs.json"):
            with open("locs.json", "r") as f:
                self.locs = json.load(f)

    async def on_user_join(self, user: User, pos: Position) -> None:
        await self.highrise.chat(f"Привет, @{user.username}!")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()
        
        if msg.startswith("сейв "):
            name = msg.split(" ", 1)[1]
            room_users = await self.highrise.get_room_users()
            for u, p in room_users.content:
                if u.id == user.id and isinstance(p, Position):
                    self.locs[name] = [p.x, p.y, p.z, p.facing]
                    with open("locs.json", "w") as f: json.dump(self.locs, f)
                    await self.highrise.chat(f"Точка {name} сохранена!")

        elif msg.startswith("тп ") or msg == "вип":
            loc = "вип" if msg == "вип" else msg.split(" ", 1)[1]
            if loc in self.locs:
                p = self.locs[loc]
                await self.highrise.teleport(user.id, Position(p[0], p[1], p[2], p[3]))

        elif msg.isdigit():
            await self.highrise.send_emote(msg, user.id)

def run_web():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    room_id = "6300a02c6c0f7d15f7a783b6"
    api_key = os.environ.get("API_KEY")
    
    if api_key:
        definitions = [("main:MyBot", room_id, api_key)]
        asyncio.run(main(definitions))
    else:
        print("Ключ API_KEY не найден!")
