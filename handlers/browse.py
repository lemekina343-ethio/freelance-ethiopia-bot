from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from google_sheets import get_open_jobs, add_lead, get_active_freelancers, add_rating, get_freelancer_rating

router = Router()

def rating_text(user_id):
    avg, count = get_freelancer_rating(user_id)
    if avg is None:
        return "⭐ No ratings yet"
    return f"⭐ {avg} ({count} review{'s' if count != 1 else ''})"

def freelancer_caption(f):
    avg_text = rating_text(f["user_id"])
    return (
        f"👤 {f.get('name', 'N/A')}\n"
        f"{avg_text}\n"
        f"Category: {f.get('category', 'N/A')}\n"
        f"Skills: {f.get('skills', 'N/A')}\n"
        f"Experience: {f.get('experience', 'N/A')}\n"
        f"Rate: {f.get('rate', 'N/A')}\n"
        f"Location: {f.get('location', 'N/A')}"
    )

def freelancer_keyboard(user_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="📞 Contact", callback_data=f"contactfl_{user_id}")
    kb.button(text="⭐ Rate", callback_data=f"rate_{user_id}")
    kb.adjust(2)
    return kb.as_markup()

def stars_keyboard(user_id):
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(text="⭐" * i, callback_data=f"ratestar_{user_id}_{i}")
    kb.adjust(1)
    return kb.as_markup()

async def send_freelancer_card(answer_func, f):
    file_id = f.get("portfolio_file_id")
    file_type = f.get("portfolio_file_type")
    caption = freelancer_caption(f)
    kb = freelancer_keyboard(f["user_id"])
    if file_id and file_type == "photo":
        await answer_func.answer_photo(photo=file_id, caption=caption, reply_markup=kb)
    elif file_id and file_type == "video":
        await answer_func.answer_video(video=file_id, caption=caption, reply_markup=kb)
    else:
        await answer_func.answer(caption, reply_markup=kb)

@router.message(Command("find_work"))
async def find_work(message: Message):
    jobs = get_open_jobs()
    if not jobs:
        await message.answer("No open jobs right now. Check back soon!")
        return

    for job in jobs[:5]:
        kb = InlineKeyboardBuilder()
        kb.button(text="📞 Contact", callback_data=f"contactjob_{job['job_id']}")
        kb.adjust(1)
        await message.answer(
            f"💼 {job['title']}\n"
            f"Category: {job['category']}\n"
            f"Budget: {job['budget']}\n"
            f"Location: {job['location_pref']}\n"
            f"Description: {job['description']}",
            reply_markup=kb.as_markup()
        )

@router.callback_query(F.data.startswith("contactjob_"))
async def contact_job(callback: CallbackQuery):
    job_id = callback.data.replace("contactjob_", "")
    jobs = get_open_jobs()
    job = next((j for j in jobs if j["job_id"] == job_id), None)

    if not job:
        await callback.answer("Job not found or no longer available.", show_alert=True)
        return

    add_lead(
        lead_type="job",
        ref_id=job_id,
        from_user_id=callback.from_user.id,
        to_user_id=job["client_user_id"]
    )

    await callback.message.answer(f"📇 Contact for '{job['title']}': {job['contact']}")
    await callback.answer()

@router.message(Command("find_talent"))
async def find_talent(message: Message):
    freelancers = get_active_freelancers()
    if not freelancers:
        await message.answer("No freelancers listed yet. Check back soon!")
        return

    for f in freelancers[:5]:
        await send_freelancer_card(message, f)

@router.callback_query(F.data == "browse_jobs")
async def browse_jobs_callback(callback: CallbackQuery):
    await callback.answer()
    jobs = get_open_jobs()
    if not jobs:
        await callback.message.answer("No open jobs right now. Check back soon!")
        return

    for job in jobs[:5]:
        kb = InlineKeyboardBuilder()
        kb.button(text="📞 Contact", callback_data=f"contactjob_{job['job_id']}")
        kb.adjust(1)
        await callback.message.answer(
            f"💼 {job['title']}\n"
            f"Category: {job['category']}\n"
            f"Budget: {job['budget']}\n"
            f"Location: {job['location_pref']}\n"
            f"Description: {job['description']}",
            reply_markup=kb.as_markup()
        )

@router.callback_query(F.data == "browse_talent")
async def browse_talent_callback(callback: CallbackQuery):
    await callback.answer()
    freelancers = get_active_freelancers()
    if not freelancers:
        await callback.message.answer("No freelancers listed yet. Check back soon!")
        return

    for f in freelancers[:5]:
        await send_freelancer_card(callback.message, f)

@router.callback_query(F.data.startswith("contactfl_"))
async def contact_freelancer(callback: CallbackQuery):
    fl_user_id = callback.data.replace("contactfl_", "")
    freelancers = get_active_freelancers()
    f = next((x for x in freelancers if str(x["user_id"]) == fl_user_id), None)

    if not f:
        await callback.answer("Freelancer not found or no longer listed.", show_alert=True)
        return

    add_lead(
        lead_type="freelancer",
        ref_id=fl_user_id,
        from_user_id=callback.from_user.id,
        to_user_id=f["user_id"]
    )

    await callback.message.answer(f"📇 Contact for {f['name']}: {f['contact']}")
    await callback.answer()

@router.callback_query(F.data.startswith("rate_"))
async def rate_freelancer_start(callback: CallbackQuery):
    fl_user_id = callback.data.replace("rate_", "")
    if str(callback.from_user.id) == fl_user_id:
        await callback.answer("You can't rate yourself.", show_alert=True)
        return
    await callback.message.answer("How many stars would you give?", reply_markup=stars_keyboard(fl_user_id))
    await callback.answer()

@router.callback_query(F.data.startswith("ratestar_"))
async def rate_freelancer_save(callback: CallbackQuery):
    _, fl_user_id, stars = callback.data.split("_")
    add_rating(
        freelancer_user_id=fl_user_id,
        from_user_id=callback.from_user.id,
        stars=int(stars)
    )
    await callback.message.edit_text(f"✅ Thanks for rating! You gave {'⭐' * int(stars)}")
    await callback.answer()