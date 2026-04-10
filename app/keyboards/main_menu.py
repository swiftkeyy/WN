from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.utils.constants import MODE_TITLES


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🪄 Удалить фон', callback_data='menu:remove_bg')
    builder.button(text='👤 Сделать аватар', callback_data='menu:avatar')
    builder.button(text='🎬 Сделать постер', callback_data='menu:poster')
    builder.button(text='🎟 Сделать стикеры', callback_data='menu:stickers')
    builder.button(text='🛍 Оформить товар', callback_data='menu:product')
    builder.button(text='🕘 История', callback_data='menu:history')
    builder.button(text='❓ Помощь', callback_data='menu:help')
    builder.adjust(1, 2, 2, 2)
    return builder.as_markup()



def style_keyboard(mode: str, items: Sequence[tuple[str, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for style_key, title in items:
        builder.button(text=title, callback_data=f'style:{mode}:{style_key}')
    builder.button(text='⬅️ Назад в меню', callback_data='menu:home')
    builder.adjust(2, 2, 1)
    return builder.as_markup()



def history_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅️ В меню', callback_data='menu:home')
    return builder.as_markup()



def processing_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅️ В меню', callback_data='menu:home')
    return builder.as_markup()



def photo_request_keyboard(mode: str, style_key: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if style_key:
        builder.button(text='🔁 Сменить стиль', callback_data=f'menu:{mode}')
    builder.button(text='⬅️ В меню', callback_data='menu:home')
    builder.adjust(1)
    return builder.as_markup()



def mode_title(mode: str) -> str:
    return MODE_TITLES.get(mode, mode)
