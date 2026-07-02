from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from google_sheets import get_all_freelancers, get_all_jobs

router = Router()

@router.message(Command("my_profile"))
async def my_profile(message: Message):
    user_id = message.from_user.id
    freelancers = get_all_freelancers()
    my_entries = [f for f in freelancers if str(f.get("user_id")) == str(user_id)]

    if not my_entries:
        await message.answer("You don't have a freelancer profile yet. Tap 'Find work' from /start to create one.")
        return

    latest = my_entries[-1]
    await message.answer(
        f"👤 Your Profile\n\n"
        f"Name: {latest.get('name', 'N/A')}\n"
        f"Category: {latest.get('category', 'N/A')}\n"
        f"Skills: {latest.get('skills', 'N/A')}\n"
        f"Experience: {latest.get('experience', 'N/A')}\n"
        f"Portfolio: {latest.get('portfolio_links', 'N/A')}\n"
        f"Location: {latest.get('location', 'N/A')}\n"
        f"Rate: {latest.get('rate', 'N/A')}\n"
        f"Contact: {latest.get('contact', 'N/A')}\n"
        f"Status: {latest.get('status', 'N/A')}\n\n"
        f"To update your profile, tap 'Find work' from /start and submit again — your newest info will be shown here."
    )

@router.message(Command("my_jobs"))
async def my_jobs(message: Message):
    user_id = message.from_user.id
    jobs = get_all_jobs()
    my_entries = [j for j in jobs if str(j.get("client_user_id")) == str(user_id)]

    if not my_entries:
        await message.answer("You haven't posted any jobs yet. Tap 'Hire talent' from /start to post one.")
        return

    for job in my_entries[-5:]:
        await message.answer(
            f"💼 {job.get('title', 'N/A')} ({job.get('status', 'N/A')})\n"
            f"Category: {job.get('category', 'N/A')}\n"
            f"Budget: {job.get('budget', 'N/A')}\n"
            f"Location: {job.get('location_pref', 'N/A')}\n"
            f"Description: {job.get('description', 'N/A')}\n"
            f"Posted: {job.get('created_at', 'N/A')}"
        )

@router.callback_query(F.data == "my_profile")
async def my_profile_callback(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    freelancers = get_all_freelancers()
    my_entries = [f for f in freelancers if str(f.get("user_id")) == str(user_id)]

    if not my_entries:
        await callback.message.answer("You don't have a freelancer profile yet. Tap 'Find work' to create one.")
        return

    latest = my_entries[-1]
    await callback.message.answer(
        f"👤 Your Profile\n\n"
        f"Name: {latest.get('name', 'N/A')}\n"
        f"Category: {latest.get('category', 'N/A')}\n"
        f"Skills: {latest.get('skills', 'N/A')}\n"
        f"Experience: {latest.get('experience', 'N/A')}\n"
        f"Portfolio: {latest.get('portfolio_links', 'N/A')}\n"
        f"Location: {latest.get('location', 'N/A')}\n"
        f"Rate: {latest.get('rate', 'N/A')}\n"
        f"Contact: {latest.get('contact', 'N/A')}\n"
        f"Status: {latest.get('status', 'N/A')}\n\n"
        f"To update your profile, tap 'Find work' and submit again — your newest info will be shown here."
    )

@router.callback_query(F.data == "my_jobs")
async def my_jobs_callback(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    jobs = get_all_jobs()
    my_entries = [j for j in jobs if str(j.get("client_user_id")) == str(user_id)]

    if not my_entries:
        await callback.message.answer("You haven't posted any jobs yet. Tap 'Hire talent' to post one.")
        return

    for job in my_entries[-5:]:
        await callback.message.answer(
            f"💼 {job.get('title', 'N/A')} ({job.get('status', 'N/A')})\n"
            f"Category: {job.get('category', 'N/A')}\n"
            f"Budget: {job.get('budget', 'N/A')}\n"
            f"Location: {job.get('location_pref', 'N/A')}\n"
            f"Description: {job.get('description', 'N/A')}\n"
            f"Posted: {job.get('created_at', 'N/A')}"
        )