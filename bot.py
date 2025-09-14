import logging
import logging.config
import os
import asyncio

from pyrogram import Client, __version__, idle, errors
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

# ----------------- Logging Config -----------------
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# ----------------- Constants -----------------
PORT = "8080"

# ----------------- Start Bot -----------------
LazyPrincessBot.start()

async def Lazy_start():
    try:
        print('\n')
        print(' Initalizing Telegram Bot ')

        if not os.path.isdir(DOWNLOAD_LOCATION):
            os.makedirs(DOWNLOAD_LOCATION)

        # Bot info
        bot_info = await LazyPrincessBot.get_me()
        LazyPrincessBot.username = bot_info.username

        # Extra clients
        await initialize_clients()

        # Keepalive for Heroku
        if ON_HEROKU:
            asyncio.create_task(ping_server())

        # Banned users/chats
        b_users, b_chats, lz_verified = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        temp.LAZY_VERIFIED_CHATS = lz_verified

        # DB Index
        await Media.ensure_indexes()

        # Current Bot info for templates
        me = await LazyPrincessBot.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        LazyPrincessBot.username = '@' + me.username

        # Web server setup
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
        await web.TCPSite(app, bind_address, PORT).start()

        # Log success
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

        # Keep alive until stop
        await idle()

    except errors.FloodWait as e:
        logging.warning(f"FloodWait detected! Sleeping for {e.value} seconds...")
        await asyncio.sleep(e.value)
        await Lazy_start()   # Restart after wait

    except Exception as e:
        logging.error(f"Unexpected error in bot: {e}", exc_info=True)
        # Restart loop after error
        await asyncio.sleep(5)
        await Lazy_start()


if __name__ == '__main__':
    try:
        asyncio.run(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
