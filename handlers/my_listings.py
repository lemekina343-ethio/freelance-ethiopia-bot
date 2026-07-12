from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from states import EditProfile
from google_sheets import get_all_freelancers, get_all_jobs, update_freelancer_field

router = Router()

from aiogram.types import FSInputFile

@router.message(Command("my_profile"))
async def my_profile(message: Message):
    user_id = message.from_user.id
    freelancers = get_all_freelancers()
    my_entries = [f for f in freelancers if str(f.get("user_id")) == str(user_id)]

    if not my_entries:
        await message.answer("You don't have a freelancer profile yet. Tap 'Find work' from /start to create one.")
        return

    latest = my_entries[-1]
    caption = (
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
        f"To update, send /edit_profile"
    )
    file_id = latest.get("portfolio_file_id")
    file_type = latest.get("portfolio_file_type")
    if file_id and file_type == "photo":
        await message.answer_photo(photo=file_id, caption=caption)
    elif file_id and file_type == "video":
        await message.answer_video(video=file_id, caption=caption)
    else:
        await message.answer(caption)

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
    caption = (
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
        f"To update, send /edit_profile"
    )
    file_id = latest.get("portfolio_file_id")
    file_type = latest.get("portfolio_file_type")
    if file_id and file_type == "photo":
        await callback.message.answer_photo(photo=file_id, caption=caption)
    elif file_id and file_type == "video":
        await callback.message.answer_video(video=file_id, caption=caption)
    else:
        await callback.message.answer(caption)
        
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
        f"To update, send /edit_profile"
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

def edit_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Name", callback_data="editfl_name")
    kb.button(text="🏷 Category", callback_data="editfl_category")
    kb.button(text="🛠 Skills", callback_data="editfl_skills")
    kb.button(text="📈 Experience", callback_data="editfl_experience")
    kb.button(text="🔗 Portfolio", callback_data="editfl_portfolio_links")
    kb.button(text="📍 Location", callback_data="editfl_location")
    kb.button(text="💰 Rate", callback_data="editfl_rate")
    kb.button(text="📞 Contact", callback_data="editfl_contact")
    kb.adjust(2)
    return kb.as_markup()

@router.message(Command("edit_profile"))
async def edit_profile_start(message: Message):
    freelancers = get_all_freelancers()
    my_entries = [f for f in freelancers if str(f.get("user_id")) == str(message.from_user.id)]
    if not my_entries:
        await message.answer("You don't have a profile yet. Tap 'Find work' from /start to create one.")
        return
    await message.answer("What would you like to update?", reply_markup=edit_menu_keyboard())

@router.callback_query(F.data.startswith("editfl_"))
async def edit_field_select(callback: CallbackQuery, state: FSMContext):
    field = callback.data.replace("editfl_", "")
    await state.update_data(field=field)
    await state.set_state(EditProfile.waiting_for_value)
    field_labels = {
        "name": "your name", "category": "your category", "skills": "your skills",
        "experience": "your experience level", "portfolio_links": "your portfolio link",
        "location": "your location", "rate": "your rate", "contact": "your contact info"
    }
    await callback.message.edit_text(f"Send the new value for {field_labels.get(field, field)}:")
    await callback.answer()

@router.message(EditProfile.waiting_for_value)
async def edit_field_save(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    success = update_freelancer_field(message.from_user.id, field, message.text)
    if success:
        await message.answer("✅ Updated! Send /my_profile to see your latest info.")
    else:
        await message.answer("Something went wrong — couldn't find your profile to update.")
    await state.clear()