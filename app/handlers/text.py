from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.ai.gemini_client import GeminiClient
from app.handlers.states import BotStates
from app.keyboards.main_menu import build_main_menu_keyboard

router = Router()
gemini_client = GeminiClient()


MODE_TITLES = {
    "remove_bg": "Удалить фон",
    "avatar": "Сделать аватар",
    "poster": "Сделать постер",
    "stickers": "Сделать стикеры",
    "product": "Оформить товар",
}


@router.message(BotStates.waiting_for_photo, F.text & ~F.text.startswith("/"))
async def save_user_text_for_mode(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    data = await state.get_data()
    mode = data.get("mode", "avatar")

    await state.update_data(user_text=text)

    await message.answer(
        f"Пожелание для режима «{MODE_TITLES.get(mode, mode)}» сохранено.\n"
        f"Теперь пришли фото.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text & ~F.text.startswith("/"))
async def free_text_router_handler(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    mode = await gemini_client.classify_request(text)

    helper_text = await gemini_client.generate_helper_reply(mode, text)

    await message.answer(
        helper_text,
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Выбери действие:",
        reply_markup=build_main_menu_keyboard(),
    )
