import logging
import logging.config
import asyncio
import os
import requests   # ✅ Self-ping के लिए requests चाहिए
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web
from plugins import web_server
from pyrogram import idle
from lazybot import LazyPrincessBot
from lazybot.clients import initialize_clients

# -------------------- Existing Configurations --------------------
PORT = "8080"
LazyPrincessBot.start()
loop = asyncio.get_event_loop()

# ✅ SELF-PING URL (अगर future में नया deploy करो तो यहाँ URL update करना होगा)
KOYEB_APP_URL = "https://advisory-kristin-akenwat212-5bf25557.koyeb.app/"

# ✅ Self-ping function (हर 10 मिनट में खुद को ping करेगा ताकि idle timeout न आए)
async def self_ping():
    while True:
        try:
            logging.info(f"🔄 Self-ping → {KOYEB_APP_URL}")
            requests.get(KOYEB_APP_URL)
        except Exception as e:
            logging.warning(f"⚠️ Ping failed: {e}")
        await asyncio.sleep(600)  # हर 10 मिनट = 600 सेकंड में ping

async def Lazy_start():
    print('\n')
    print(' Initalizing Telegram Bot ')
    
    # ✅ Existing folder check
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)
    
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username
    
    # ✅ Initialize extra clients
    await initialize_clients()
    
    # ✅ Self-ping को हमेशा enable कर दिया (Heroku हो या Koyeb, दोनों में काम करेगा)
    asyncio.create_task(self_ping())
    
    # ✅ Existing banned users & chats load
    b_users, b_chats , lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified
    
    # ✅ Media DB Index ensure
    await Media.ensure_indexes()
    
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    
    # ✅ Existing aiohttp web server (जैसे का तैसा रहेगा)
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if ON_HEROKU else BIND_ADRESS
    await web.TCPSite(app, bind_address, PORT).start()
    
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    
    # ✅ Start bot idle mode
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(Lazy_start())
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
