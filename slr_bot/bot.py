import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import begin, rating

load_dotenv('.env')

logging.basicConfig(level=logging.INFO)

async def start():
    bot = Bot(token=os.environ['BOT_TOKEN'])
    dp = Dispatcher()

    dp.include_routers(begin.router, rating.router)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
