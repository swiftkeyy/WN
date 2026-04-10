from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    waiting_for_remove_bg_photo = State()
    waiting_for_prompt_text = State()
    waiting_for_template_input = State()
