from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.keyboards.main_menu import MAIN_MENU
from app.keyboards.templates_menu import build_categories_keyboard, build_templates_keyboard
from app.services.history_service import HistoryService
from app.services.template_service import TemplateService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions

router = Router()
template_service = TemplateService()
user_service = UserService()
history_service = HistoryService()


@router.message(F.text == 'Трендовые шаблоны')
async def templates_entrypoint(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        categories = await template_service.list_categories(session)
    if not categories:
        await message.answer('Шаблоны пока не загружены.', reply_markup=MAIN_MENU)
        return
    await message.answer('Выбери категорию:', reply_markup=build_categories_keyboard(categories))


@router.callback_query(F.data.startswith('tplcat:'))
async def template_category_selected(callback: CallbackQuery) -> None:
    category = callback.data.split(':', maxsplit=1)[1]
    async with AsyncSessionLocal() as session:
        templates = await template_service.list_by_category(session, category)
    items = [(template.key, template.title) for template in templates]
    await callback.message.edit_text(
        f'Категория: {category}\nВыбери шаблон:',
        reply_markup=build_templates_keyboard(items),
    )
    await callback.answer()


@router.callback_query(F.data == 'tpl:back_to_categories')
async def template_back(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        categories = await template_service.list_categories(session)
    await callback.message.edit_text('Выбери категорию:', reply_markup=build_categories_keyboard(categories))
    await callback.answer()


@router.callback_query(F.data.startswith('tpl:'))
async def template_selected(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(':', maxsplit=1)[1]
    if key == 'back_to_categories':
        return

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, callback.from_user)
        template = await template_service.get_by_key(session, key)
        if template is None:
            await callback.answer('Шаблон не найден', show_alert=True)
            return
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.TEMPLATE_SELECTED,
            payload_json={'template_key': key},
        )

    await state.set_state(BotStates.waiting_for_template_input)
    await state.update_data(template_key=key)
    await callback.message.answer(
        f'Шаблон: {template.title}\n\nПришли текст или фото. Я соберу финальный prompt.',
        reply_markup=MAIN_MENU,
    )
    await callback.answer()
