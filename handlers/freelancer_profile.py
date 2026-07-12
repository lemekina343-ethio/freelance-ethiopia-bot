from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import FreelancerOnboarding
from google_sheets import add_freelancer

router = Router()

CATEGORIES = ["Graphic Design", "Web Dev", "Writing & Translation", "Video & Animation", "Voice Over", "Modeling", "Data Entry", "Virtual Assistant", "Other"]
LOCATIONS = ["Addis Ababa", "Other city", "Remote (anywhere in Ethiopia)"]

def category_keyboard():
    kb = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        kb.button(text=cat, callback_data=f"cat_{cat}")
    kb.adjust(1)
    return kb.as_markup()

def experience_keyboard():
    kb = InlineKeyboardBuilder()
    for level in ["Beginner", "Intermediate", "Expert"]:
        kb.button(text=level, callback_data=f"exp_{level}")
    kb.adjust(3)
    return kb.as_markup()

def location_keyboard():
    kb = InlineKeyboardBuilder()
    for loc in LOCATIONS:
        kb.button(text=loc, callback_data=f"loc_{loc}")
    kb.adjust(1)
    return kb.as_markup()

@router.callback_query(F.data == "role_freelancer")
async def start_freelancer_onboarding(callback, state: FSMContext):
    await state.set_state(FreelancerOnboarding.name)
    await callback.message.edit_text("Great! Let's set up your profile.\n\nWhat's your full name?")
    await callback.answer()

@router.message(FreelancerOnboarding.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FreelancerOnboarding.category)
    await message.answer("What's your main category?", reply_markup=category_keyboard())

@router.callback_query(FreelancerOnboarding.category, F.data.startswith("cat_"))
async def process_category(callback, state: FSMContext):
    category = callback.data.replace("cat_", "")
    await state.update_data(category=category)
    await state.set_state(FreelancerOnboarding.skills)
    await callback.message.edit_text(f"Category: {category}\n\nList your top 3-5 skills (comma separated).")
    await callback.answer()

@router.message(FreelancerOnboarding.skills)
async def process_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(FreelancerOnboarding.experience)
    await message.answer("What's your experience level?", reply_markup=experience_keyboard())

@router.callback_query(FreelancerOnboarding.experience, F.data.startswith("exp_"))
async def process_experience(callback, state: FSMContext):
    experience = callback.data.replace("exp_", "")
    await state.update_data(experience=experience)
    await state.set_state(FreelancerOnboarding.portfolio)
    await callback.message.edit_text(
        f"Experience: {experience}\n\nShare a link to your work (Google Drive, Behance, GitHub, YouTube, etc.) or type 'none'."
    )
    await callback.answer()

@router.message(FreelancerOnboarding.portfolio)
async def process_portfolio(message: Message, state: FSMContext):
    await state.update_data(portfolio=message.text)
    await state.set_state(FreelancerOnboarding.portfolio_media)
    await message.answer(
        "Want to show a sample of your work? Send *one* photo or video now, or type 'skip'.\n\n_(If you send more than one, only the first will be saved.)_",
        parse_mode="Markdown"
    )

@router.message(FreelancerOnboarding.portfolio_media, F.photo)
async def process_portfolio_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("media_received"):
        return
    await state.update_data(media_received=True)
    file_id = message.photo[-1].file_id
    await state.update_data(portfolio_file_id=file_id, portfolio_file_type="photo")
    await state.set_state(FreelancerOnboarding.location)
    await message.answer("Got it! Where are you based?", reply_markup=location_keyboard())

@router.message(FreelancerOnboarding.portfolio_media, F.video)
async def process_portfolio_video(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("media_received"):
        return
    await state.update_data(media_received=True)
    file_id = message.video.file_id
    await state.update_data(portfolio_file_id=file_id, portfolio_file_type="video")
    await state.set_state(FreelancerOnboarding.location)
    await message.answer("Got it! Where are you based?", reply_markup=location_keyboard())

@router.message(FreelancerOnboarding.portfolio_media)
async def process_portfolio_skip(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("media_received"):
        return
    await state.update_data(media_received=True, portfolio_file_id="", portfolio_file_type="")
    await state.set_state(FreelancerOnboarding.location)
    await message.answer("No problem! Where are you based?", reply_markup=location_keyboard())

@router.message(FreelancerOnboarding.portfolio_media)
async def process_portfolio_skip(message: Message, state: FSMContext):
    await state.update_data(portfolio_file_id="", portfolio_file_type="")
    await state.set_state(FreelancerOnboarding.location)
    await message.answer("No problem! Where are you based?", reply_markup=location_keyboard())

@router.callback_query(FreelancerOnboarding.location, F.data.startswith("loc_"))
async def process_location(callback, state: FSMContext):
    location = callback.data.replace("loc_", "")
    await state.update_data(location=location)
    await state.set_state(FreelancerOnboarding.rate)
    await callback.message.edit_text(
        f"Location: {location}\n\nWhat's your typical rate? (e.g. 500 ETB/hour or 3000 ETB/project)"
    )
    await callback.answer()

@router.message(FreelancerOnboarding.rate)
async def process_rate(message: Message, state: FSMContext):
    await state.update_data(rate=message.text)
    await state.set_state(FreelancerOnboarding.contact)
    await message.answer("How should clients contact you? (Telegram username, phone, or email)")

@router.message(FreelancerOnboarding.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    user_id = message.from_user.id

    add_freelancer(
        user_id=user_id,
        name=data["name"],
        category=data["category"],
        skills=data["skills"],
        experience=data["experience"],
        portfolio=data["portfolio"],
        location=data["location"],
        rate=data["rate"],
        contact=message.text,
        portfolio_file_id=data.get("portfolio_file_id", ""),
        portfolio_file_type=data.get("portfolio_file_type", "")
    )

    caption = (
        f"✅ Profile saved!\n\n"
        f"Name: {data['name']}\n"
        f"Category: {data['category']}\n"
        f"Skills: {data['skills']}\n"
        f"Experience: {data['experience']}\n"
        f"Portfolio: {data['portfolio']}\n"
        f"Location: {data['location']}\n"
        f"Rate: {data['rate']}\n"
        f"Contact: {message.text}\n\n"
        f"You're now listed! Clients will be able to find you."
    )

    file_id = data.get("portfolio_file_id")
    file_type = data.get("portfolio_file_type")
    if file_id and file_type == "photo":
        await message.answer_photo(photo=file_id, caption=caption)
    elif file_id and file_type == "video":
        await message.answer_video(video=file_id, caption=caption)
    else:
        await message.answer(caption)

    await state.clear()