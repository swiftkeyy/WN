from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.ai.gemini_client import GeminiClient
from app.handlers.states import BotStates
from app.keyboards.main_menu import build_main_menu_keyboard, mode_title

router = Router()
gemini_client = GeminiClient()


STYLE_HINTS = {
    "avatar": ["old money", "cyberpunk", "anime", "fashion", "luxury"],
    "poster": ["cinematic", "action", "dark", "brand", "youtube"],
    "stickers": ["мемно", "мило", "аниме", "мультяшно"],
    "product": ["luxury", "minimal", "marketplace", "ad"],
}


@router.message(BotStates.waiting_for_photo, F.text & ~F.text.startswith("/"))
async def save_user_text_for_mode(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    data = await state.get_data()
    mode = data.get("mode", "avatar")

    style_key = ""
    lowered = text.lower()

    for hint in STYLE_HINTS.get(mode, []):
        if hint.lower() in lowered:
            style_key = hint
            break

    await state.update_data(
        user_text=text,
        style_key=style_key,
    )

    await message.answer(
        f"Пожелание для режима «{mode_title(mode)}» сохранено.\nТеперь пришли фото.",
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
