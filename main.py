import asyncio
import os
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.__main__ import main

class MyBot(BaseBot):
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        # position добавлен, TypeError больше не будет
        try:
            await self.highrise.chat(f"Hello @{user.username}!")
        except:
            pass

    async def on_chat(self, user: User, message: str) -> None:
        if message.isdigit():
            await self.highrise.send_emote(message, user.id)

if __name__ == "__main__":
    room_id = "69b56b7ebacc85f7998d47a9"
    api_key = os.environ.get("API_KEY")
    if api_key:
        definitions = [("main:MyBot", room_id, api_key)]
        asyncio.run(main(definitions))
