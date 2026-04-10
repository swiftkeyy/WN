from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.keyboards.templates_menu import (
    build_template_categories_keyboard,
    build_templates_keyboard,
)
from app.services.template_service import TemplateService

router = Router()
template_service = TemplateService()


async def safe_edit_text(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
) -> None:
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as exc:
        error_text = str(exc).lower()
        if "message is not modified" in error_text:
            await callback.answer("Уже открыто")
            return
        raise
    await callback.answer()


@router.message(F.text == "Трендовые шаблоны")
async def templates_entrypoint(message: Message, state: FSMContext) -> None:
    await state.clear()

    async with AsyncSessionLocal() as session:
        categories = await template_service.list_categories(session)

    if not categories:
        await message.answer("Шаблоны пока не загружены.")
        return

    await message.answer(
        "Выбери категорию шаблонов:",
        reply_markup=build_template_categories_keyboard(categories),
    )


@router.callback_query(F.data.startswith("tplcat:"))
async def template_category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    if not callback.data:
        await callback.answer()
        return

    category = callback.data.split(":", 1)[1]

    async with AsyncSessionLocal() as session:
        templates = await template_service.list_by_category(session, category)

    if not templates:
        await safe_edit_text(
            callback,
            "В этой категории пока нет шаблонов.",
            reply_markup=None,
        )
        return

    await safe_edit_text(
        callback,
        f"Категория: {category}\n\nВыбери шаблон:",
        reply_markup=build_templates_keyboard(templates),
    )


@router.callback_query(F.data.startswith("tpl:"))
async def template_selected(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data:
        await callback.answer()
        return

    template_key = callback.data.split(":", 1)[1]

    await state.set_state(BotStates.waiting_for_template_input)
    await state.update_data(template_key=template_key)

    await safe_edit_text(
        callback,
        "Шаблон выбран.\n\nТеперь пришли текст или фото, и я соберу финальный prompt.",
        reply_markup=None,
    )
