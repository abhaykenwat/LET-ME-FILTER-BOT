import asyncio
import logging
from aiohttp import web
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import FloodWait

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from plugins import web_server
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

PORT = "8080"

async def Lazy_start():
    try:
        print(" Initalizing Telegram Bot ")

        # Bot start karna bhi yahi loop me
        await LazyPrincessBot.start()

        # Bot info
        bot_info = await LazyPrincessBot.get_me()
        LazyPrincessBot.username = bot_info.username

        # Clients
        await initialize_clients()

        if ON_HEROKU:
            asyncio.create_task(ping_server())

        # Banned users/chats
        b_users, b_chats, lz_verified = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        temp.LAZY_VERIFIED_CHATS = lz_verified

        await Media.ensure_indexes()

        # Web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        print(f"{bot_info.first_name} started with Pyrogram v{__version__} (Layer {layer})")

        await idle()

    except FloodWait as e:
        print(f"FloodWait {e.value} sec, sleeping...")
        await asyncio.sleep(e.value)
        await Lazy_start()

    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        await asyncio.sleep(5)
        await Lazy_start()

    finally:
        await LazyPrincessBot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(Lazy_start())
    except KeyboardInterrupt:
        print("Service stopped.")
