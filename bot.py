import logging
import logging.config
import os
import asyncio
from pyrogram import __version__, idle
from aiohttp import web

from lazybot import LazyPrincessBot
from plugins import web_server
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from lazybot.clients import initialize_clients
from util.keepalive import ping_server

# ---------------- Logging ---------------- #
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, force=True)

# ---------------- Constants ---------------- #
PORT = 8080
BIND_ADDRESS = "0.0.0.0" if ON_HEROKU else BIND_ADRESS

# ---------------- Bot Start ---------------- #
async def Lazy_start():
    print("\nInitializing Telegram Bot...")

    # Ensure download folder exists
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    # Start Pyrogram client
    await LazyPrincessBot.start()
    me = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = '@' + me.username
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    # Initialize any extra clients
    await initialize_clients()

    # Ping server if on Heroku/Koyeb
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Load banned users/chats inside same loop
    b_users, b_chats, lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified

    # Ensure DB indexes
    await Media.ensure_indexes()

    # Start web server
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    await web.TCPSite(app_runner, BIND_ADDRESS, PORT).start()

    logging.info(f"{me.first_name} running Pyrogram v{__version__} on {LazyPrincessBot.username}")
    logging.info(LOG_STR)

    # Keep bot alive
    await idle()

# ---------------- Main Loop ---------------- #
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
