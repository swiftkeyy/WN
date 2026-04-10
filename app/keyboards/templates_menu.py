from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.models import PromptTemplate


def build_template_categories_keyboard(categories: Sequence[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category.replace("_", " ").title(),
            callback_data=f"tplcat:{category}",
        )

    builder.adjust(2)
    return builder.as_markup()


def build_templates_keyboard(templates: Sequence[PromptTemplate]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for template in templates:
        builder.button(
            text=template.title,
            callback_data=f"tpl:{template.key}",
        )

    builder.adjust(1)
    return builder.as_markup()
