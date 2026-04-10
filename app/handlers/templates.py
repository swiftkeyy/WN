from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.keyboards.main_menu import main_menu_keyboard, mode_title, photo_request_keyboard, style_keyboard
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, MODE_TITLES, STYLE_PRESETS

router = Router()
user_service = UserService()
history_service = HistoryService()


async def _store_selected_mode(callback: CallbackQuery, mode: str, style_key: str | None) -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, callback.from_user)
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.MODE_SELECTED,
            payload_json={'mode': mode, 'style_key': style_key},
        )


@router.callback_query(F.data == 'menu:home')
async def menu_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        'Выбери, что сделать с фото:',
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('menu:'))
async def menu_mode_selected(callback: CallbackQuery, state: FSMContext) -> None:
    mode = callback.data.split(':', 1)[1]
    if mode == 'home' or mode in {'history', 'help'}:
        return

    await state.clear()

    if mode == 'remove_bg':
        await state.set_state(BotStates.waiting_for_photo)
        await state.update_data(mode=mode, style_key=None)
        await _store_selected_mode(callback, mode, None)
        await callback.message.edit_text(
            'Пришли фото. Я удалю фон и верну готовый PNG.',
            reply_markup=photo_request_keyboard(mode),
        )
        await callback.answer()
        return

    styles = STYLE_PRESETS.get(mode, [])
    if not styles:
        await callback.answer('Этот режим пока недоступен', show_alert=True)
        return

    await callback.message.edit_text(
        f'Режим: {MODE_TITLES.get(mode, mode)}\n\nВыбери стиль:',
        reply_markup=style_keyboard(mode, styles),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('style:'))
async def style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    _, mode, style_key = callback.data.split(':', 2)
    await state.set_state(BotStates.waiting_for_photo)
    await state.update_data(mode=mode, style_key=style_key)
    await _store_selected_mode(callback, mode, style_key)

    await callback.message.edit_text(
        f'Режим: {mode_title(mode)}\nСтиль: {style_key}\n\nТеперь пришли фото.\n'
        'Если хочешь, добавь подпись к фото с пожеланиями.',
        reply_markup=photo_request_keyboard(mode, style_key),
    )
    await callback.answer()
