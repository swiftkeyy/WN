from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.keyboards.main_menu import build_main_menu_keyboard

router = Router()


HELP_TEXT = (
    "Помощь по режимам:\n\n"
    "🪄 Удалить фон — пришли фото, я уберу фон через remove.bg.\n"
    "👤 Сделать аватар — пришли фото, я сделаю стилизованный аватар.\n"
    "🎬 Сделать постер — пришли фото, я соберу постерный результат.\n"
    "🎟 Сделать стикеры — пришли фото, я подготовлю стикерный вариант.\n"
    "🛍 Оформить товар — пришли фото товара, я оформлю его как рекламный кадр.\n\n"
    "После выбора режима просто отправь фото.\n"
    "Если хочешь, можешь добавить короткое пожелание текстом."
)


@router.message(F.text == "/help")
async def help_command(message: Message) -> None:
    await message.answer(
        HELP_TEXT,
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Что делаем дальше?",
        reply_markup=build_main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu:help")
async def help_callback(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(
            HELP_TEXT,
            reply_markup=build_main_menu_keyboard(),
        )
    await callback.answer()
