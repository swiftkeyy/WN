from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


MODE_TITLES = {
    "remove_bg": "Удалить фон",
    "avatar": "Сделать аватар",
    "poster": "Сделать постер",
    "stickers": "Сделать стикеры",
    "product": "Оформить товар",
}


def mode_title(mode: str) -> str:
    return MODE_TITLES.get(mode, mode)


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🪄 Удалить фон", callback_data="menu:remove_bg")
    builder.button(text="👤 Сделать аватар", callback_data="menu:avatar")
    builder.button(text="🎬 Сделать постер", callback_data="menu:poster")
    builder.button(text="🎟 Сделать стикеры", callback_data="menu:stickers")
    builder.button(text="🛍 Оформить товар", callback_data="menu:product")
    builder.button(text="🕘 История", callback_data="menu:history")
    builder.button(text="❓ Помощь", callback_data="menu:help")

    builder.adjust(1, 2, 2, 2)
    return builder.as_markup()


def photo_request_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ В меню", callback_data="menu:root")
    return builder.as_markup()
