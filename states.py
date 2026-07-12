from aiogram.fsm.state import State, StatesGroup

class FreelancerOnboarding(StatesGroup):
    name = State()
    category = State()
    skills = State()
    experience = State()
    portfolio = State()
    portfolio_media = State()
    location = State()
    rate = State()
    contact = State()

class ClientOnboarding(StatesGroup):
    name = State()
    title = State()
    category = State()
    description = State()
    budget = State()
    location = State()
    contact = State()

class EditProfile(StatesGroup):
    waiting_for_value = State()