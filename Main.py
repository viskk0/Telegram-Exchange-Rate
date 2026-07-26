from config import TOKEN, PROXY_CONTROL

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.handlers import router, init_db
from os import path

import logging
import asyncio

session = AiohttpSession(proxy=PROXY_CONTROL)

bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    if not path.isfile("exchange_rate.db"): await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")