from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_categories_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=category.title(), callback_data=f'tplcat:{category}')]
        for category in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_templates_keyboard(items: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f'tpl:{key}')]
        for key, title in items
    ]
    rows.append([InlineKeyboardButton(text='← Категории', callback_data='tpl:back_to_categories')])
    return InlineKeyboardMarkup(inline_keyboard=rows)
