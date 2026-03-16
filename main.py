import asyncio
import sys
from flask import Flask
from threading import Thread
from highrise import BaseBot, User, Position
from highrise.__main__ import main

# === ТВОИ ДАННЫЕ ===
ROOM_ID = "69b56b7ebacc85f7998d47a9"
API_TOKEN = "e34294858f8d5399107b82349ec64bd01cbd4b46fa18562340eeb1fd219c1572"
# ===================

app = Flask('')

@app.route('/')
def home():
    return "Sugux Bot is Running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

class MyBot(BaseBot):
    emotes = [
        "emote-hello", "emote-wave", "emote-shy", "emote-sad", "emote-laughing", "emote-tired", "emote-kiss", "emote-hug", "emote-love", "emote-angry",
        "emote-confused", "emote-think", "emote-no", "emote-yes", "emote-hot", "dance-tiktok", "dance-pancakes", "dance-revelations", "dance-blackpink", "dance-pennywise",
        "dance-shoppingcart", "dance-russian", "dance-orange-justice", "emote-pose1", "emote-pose3", "emote-pose5", "emote-pose7", "emote-pose8", "emote-cutey", "emote-lust",
        "emote-greedy", "emote-bow", "emote-curtsy", "emote-float", "emote-teleporting", "emote-gift", "emote-snowball", "emote-monster_fail", "emote-paws_up", "emote-headache",
        "emote-death", "emote-cold", "emote-claps", "emote-slap", "emote-check-it", "emote-peace", "idle-loop-sitfloor", "idle-loop-aerobics", "idle-dance-casual", "idle-dance-swingy",
        "emote-sneeze", "emote-jump", "emote-faint", "emote-panic", "emote-shaking", "emote-ghost-idle", "emote-vampire-idle", "emote-energy-ball", "emote-fireball", "emote-levitate",
        "emote-exasperated", "emote-superpunch", "emote-fist-pump", "emote-celebration-step", "emote-fashion-runway", "emote-model", "emote-duckwalk", "emote-gangnam-style", "emote-macarena", "emote-shuffle",
        "emote-zombie", "dance-spiritual", "dance-smooth-operator", "dance-hands-up", "dance-breakdance", "emote-bunny-hop", "emote-skipping", "emote-moonwalk", "emote-side-to-side", "emote-spinning",
        "emote-ballet", "emote-kick-flip", "emote-handstand", "emote-robot", "emote-dab", "emote-tpose", "emote-heart-fingers", "emote-shrug", "emote-facepalm", "emote-mic-drop",
        "emote-flex", "emote-jingle-bells", "emote-turkey", "emote-scared", "emote-the-wave", "emote-hero", "emote-superman", "emote-wings", "emote-float", "emote-snake",
        "emote-frog", "emote-peekaboo", "emote-clumsy", "emote-furious", "emote-heart-shape", "emote-together", "emote-stinky", "emote-silly", "emote-smugly", "emote-think-hard",
        "emote-disappointed", "emote-crying", "emote-joy", "emote-laugh-crying", "emote-exploding-head", "emote-money-eyes", "emote-angel", "emote-devil", "emote-clown", "emote-star-struck",
        "emote-wink", "emote-tongue-out", "emote-sleeping", "emote-surprised", "emote-nerd", "emote-cool", "emote-partying", "emote-birthday", "emote-cheering", "dance-wild",
        "dance-pop", "dance-disco", "dance-hiphop", "dance-samba", "dance-ballet-spin", "dance-jazz", "dance-tap", "dance-robot-v2", "dance-electric", "emote-flex-muscles",
        "emote-weightlifting", "emote-boxing", "emote-kungfu", "emote-karate-kick", "emote-ninja", "emote-meditation", "emote-yoga", "emote-stretching", "emote-running", "emote-victory",
        "emote-winner", "emote-loser", "emote-shame", "emote-applause", "emote-curtain-call", "emote-magic-trick", "emote-mind-blown", "emote-hypnotized", "emote-dizzy", "emote-guitar-solo",
        "emote-drumming", "emote-piano", "emote-singing", "emote-conducting", "emote-dancing-star", "emote-stage-pose", "emote-backflip", "emote-frontflip", "emote-cartwheel", "emote-idk",
        "emote-omg", "emote-wow", "emote-yes-sir", "emote-no-way", "emote-thinking-face", "emote-hush", "emote-stop", "emote-go", "emote-follow-me", "emote-peace-v2",
        "emote-rock-on", "emote-thumbs-up", "emote-thumbs-down", "emote-salute", "emote-prayer", "emote-begging", "emote-giving", "emote-receiving", "emote-searching", "emote-binoculars",
        "emote-magnifying-glass", "emote-pointing", "emote-scolding", "emote-hugging-self", "emote-celebrate", "emote-fireworks", "emote-confetti", "emote-cheer-v2", "emote-finished", "emote-boxer"
    ]

    async def on_start(self, session_metadata):
        print("✅ БОТ В КОМНАТЕ!")

    async def on_chat(self, user: User, message: str):
        if message.isdigit():
            idx = int(message)
            if 0 <= idx < len(self.emotes):
                await self.highrise.send_emote(self.emotes[idx], user.id)

if __name__ == "__main__":
    # Запускаем Flask на фоне
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Запускаем бота
    print("🚀 Попытка входа в Highrise...")
    sys.argv = ["highrise", "main:MyBot", ROOM_ID, API_TOKEN]
    main()
