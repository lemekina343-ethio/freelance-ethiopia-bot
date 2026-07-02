import asyncio
from aiogram import Bot
from config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print("Bot connected as:", me.username)
    await bot.session.close()

asyncio.run(main())