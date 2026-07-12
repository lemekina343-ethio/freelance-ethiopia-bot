from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states import ClientOnboarding
from google_sheets import add_job

router = Router()

CATEGORIES = ["Graphic Design", "Web Dev", "Writing & Translation", "Video & Animation", "Voice Over", "Modeling", "Data Entry", "Virtual Assistant", "Other"]
LOCATIONS = ["Addis Ababa", "Remote (anywhere in Ethiopia)", "Other city"]

def category_keyboard():
    kb = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        kb.button(text=cat, callback_data=f"jobcat_{cat}")
    kb.adjust(1)
    return kb.as_markup()

def location_keyboard():
    kb = InlineKeyboardBuilder()
    for loc in LOCATIONS:
        kb.button(text=loc, callback_data=f"jobloc_{loc}")
    kb.adjust(1)
    return kb.as_markup()

@router.callback_query(F.data == "role_client")
async def start_client_onboarding(callback, state: FSMContext):
    await state.set_state(ClientOnboarding.name)
    await callback.message.edit_text("Great! Let's post your job.\n\nWhat's your name or company name?")
    await callback.answer()

@router.message(ClientOnboarding.name)
async def process_client_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ClientOnboarding.title)
    await message.answer("What's the job title?")

@router.message(ClientOnboarding.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ClientOnboarding.category)
    await message.answer("Which category best fits this job?", reply_markup=category_keyboard())

@router.callback_query(ClientOnboarding.category, F.data.startswith("jobcat_"))
async def process_job_category(callback, state: FSMContext):
    category = callback.data.replace("jobcat_", "")
    await state.update_data(category=category)
    await state.set_state(ClientOnboarding.description)
    await callback.message.edit_text(f"Category: {category}\n\nDescribe the work, deliverables, and timeline.")
    await callback.answer()

@router.message(ClientOnboarding.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ClientOnboarding.budget)
    await message.answer("What's your budget? (range or fixed amount)")

@router.message(ClientOnboarding.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(ClientOnboarding.location)
    await message.answer("Where would you prefer the freelancer to be based?", reply_markup=location_keyboard())

@router.callback_query(ClientOnboarding.location, F.data.startswith("jobloc_"))
async def process_job_location(callback, state: FSMContext):
    location = callback.data.replace("jobloc_", "")
    await state.update_data(location=location)
    await state.set_state(ClientOnboarding.contact)
    await callback.message.edit_text(f"Location preference: {location}\n\nHow should freelancers contact you? (Telegram username, phone, or email)")
    await callback.answer()

@router.message(ClientOnboarding.contact)
async def process_client_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id

    add_job(
        client_user_id=user_id,
        client_name=data["name"],
        title=data["title"],
        category=data["category"],
        description=data["description"],
        budget=data["budget"],
        location_pref=data["location"],
        contact=message.text
    )

    await message.answer(
        f"✅ Job posted!\n\n"
        f"Title: {data['title']}\n"
        f"Category: {data['category']}\n"
        f"Description: {data['description']}\n"
        f"Budget: {data['budget']}\n"
        f"Location preference: {data['location']}\n"
        f"Contact: {message.text}\n\n"
        f"Freelancers will be able to find and contact you."
    )
    await state.clear()