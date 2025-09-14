import logging
import logging.config
import os
import asyncio
from pyrogram import Client, __version__, idle, types
from pyrogram.raw.all import layer
from aiohttp import web

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from plugins import web_server
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

# ---------------- Logging Setup ---------------- #
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ---------------- Constants ---------------- #
PORT = 8080  # must be int
BIND_ADDRESS = "0.0.0.0" if ON_HEROKU else BIND_ADRESS

# ---------------- Bot Initialization ---------------- #
async def Lazy_start():
    print("\nInitializing Telegram Bot...")
    
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    await LazyPrincessBot.start()
    
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username

    await initialize_clients()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Load banned users and chats
    b_users, b_chats, lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified

    await Media.ensure_indexes()

    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username

    # Start web server
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, BIND_ADDRESS, PORT).start()

    logging.info(f"{me.first_name} running Pyrogram v{__version__} (Layer {layer}) on {LazyPrincessBot.username}.")
    logging.info(LOG_STR)

    await idle()


if __name__ == "__main__":
    try:
        asyncio.run(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
