import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.freelancer_profile import router as freelancer_router
from handlers.client_job import router as client_router
from handlers.browse import router as browse_router
from handlers.admin import router as admin_router
from handlers.my_listings import router as my_listings_router
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(freelancer_router)
dp.include_router(client_router)
dp.include_router(browse_router)
dp.include_router(admin_router)
dp.include_router(my_listings_router)

def role_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🧑‍💻 Find work", callback_data="role_freelancer")
    kb.button(text="📢 Hire talent", callback_data="role_client")
    kb.button(text="🔍 Browse Jobs", callback_data="browse_jobs")
    kb.button(text="🔍 Browse Talent", callback_data="browse_talent")
    kb.button(text="👤 My Profile", callback_data="my_profile")
    kb.button(text="📋 My Jobs", callback_data="my_jobs")
    kb.adjust(2, 2, 2)
    return kb.as_markup()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Welcome to Freelance Ethiopia 🇪🇹\nChoose how you want to continue:",
        reply_markup=role_keyboard()
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())