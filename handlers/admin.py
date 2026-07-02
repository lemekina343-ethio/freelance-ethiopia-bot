from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from config import ADMIN_IDS
from google_sheets import get_all_jobs, get_all_freelancers, set_job_status, set_freelancer_status

router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("admin_jobs"))
async def admin_jobs(message: Message):
    if not is_admin(message.from_user.id):
        return

    jobs = get_all_jobs()
    if not jobs:
        await message.answer("No jobs yet.")
        return

    for job in jobs[:10]:
        kb = InlineKeyboardBuilder()
        if job["status"] == "open":
            kb.button(text="🔒 Close", callback_data=f"jobclose_{job['job_id']}")
        else:
            kb.button(text="🔓 Reopen", callback_data=f"jobopen_{job['job_id']}")
        await message.answer(
            f"💼 {job['title']} ({job['status']})\n"
            f"Client: {job['client_name']}\n"
            f"Category: {job['category']}",
            reply_markup=kb.as_markup()
        )

@router.callback_query(F.data.startswith("jobclose_"))
async def job_close(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized.", show_alert=True)
        return
    job_id = callback.data.replace("jobclose_", "")
    set_job_status(job_id, "closed")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Closed.")
    await callback.answer()

@router.callback_query(F.data.startswith("jobopen_"))
async def job_open(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized.", show_alert=True)
        return
    job_id = callback.data.replace("jobopen_", "")
    set_job_status(job_id, "open")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Reopened.")
    await callback.answer()

@router.message(Command("admin_freelancers"))
async def admin_freelancers(message: Message):
    if not is_admin(message.from_user.id):
        return

    freelancers = get_all_freelancers()
    if not freelancers:
        await message.answer("No freelancers yet.")
        return

    for f in freelancers[:10]:
        kb = InlineKeyboardBuilder()
        if f["status"] == "active":
            kb.button(text="⏸ Pause", callback_data=f"flpause_{f['user_id']}")
        else:
            kb.button(text="▶️ Unpause", callback_data=f"flunpause_{f['user_id']}")
        await message.answer(
            f"👤 {f['name']} ({f['status']})\n"
            f"Category: {f['category']}",
            reply_markup=kb.as_markup()
        )

@router.callback_query(F.data.startswith("flpause_"))
async def fl_pause(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized.", show_alert=True)
        return
    user_id = callback.data.replace("flpause_", "")
    set_freelancer_status(user_id, "paused")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Paused.")
    await callback.answer()

@router.callback_query(F.data.startswith("flunpause_"))
async def fl_unpause(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Not authorized.", show_alert=True)
        return
    user_id = callback.data.replace("flunpause_", "")
    set_freelancer_status(user_id, "active")
    await callback.message.edit_text(callback.message.text + "\n\n✅ Unpaused.")
    await callback.answer()