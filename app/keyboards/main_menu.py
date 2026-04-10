from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


MODE_TITLES = {
    "remove_bg": "Удалить фон",
    "avatar": "Сделать аватар",
    "poster": "Сделать постер",
    "stickers": "Сделать стикеры",
    "product": "Оформить товар",
}


STYLE_LABELS = {
    "old_money": "Old Money",
    "cyberpunk": "Cyberpunk",
    "anime": "Anime",
    "fashion": "Fashion",
    "luxury": "Luxury",
    "cinematic": "Cinematic",
    "action": "Action",
    "dark": "Dark",
    "brand": "Brand",
    "youtube": "YouTube",
    "meme": "Мемно",
    "cute": "Мило",
    "cartoon": "Мультяшно",
    "marketplace": "Marketplace",
    "minimal": "Minimal",
    "ad": "Ad Creative",
}


MODE_STYLES = {
    "avatar": ["old_money", "cyberpunk", "anime", "fashion", "luxury"],
    "poster": ["cinematic", "action", "dark", "brand", "youtube"],
    "stickers": ["meme", "cute", "anime", "cartoon"],
    "product": ["luxury", "minimal", "marketplace", "ad"],
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


def style_keyboard(mode: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for style_key in MODE_STYLES.get(mode, []):
        builder.button(
            text=STYLE_LABELS.get(style_key, style_key),
            callback_data=f"style:{mode}:{style_key}",
        )

    builder.button(text="⏭ Без стиля", callback_data=f"style:{mode}:skip")
    builder.button(text="↩️ В меню", callback_data="menu:root")

    if mode in {"avatar", "poster", "stickers", "product"}:
        builder.adjust(2, 2, 1, 1)
    else:
        builder.adjust(1)

    return builder.as_markup()
