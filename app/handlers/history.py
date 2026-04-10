from datetime import timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import history_keyboard
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, MODE_TITLES

router = Router()
history_service = HistoryService()
user_service = UserService()


@router.callback_query(F.data == 'menu:history')
async def history_handler(callback: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, callback.from_user)
        rows = await history_service.list_recent(session, user.id)
        await history_service.log(session, user_id=user.id, action_type=HistoryActions.HISTORY_OPENED, payload_json=None)

    if not rows:
        await callback.message.edit_text('История пока пустая.', reply_markup=history_keyboard())
        await callback.answer()
        return

    lines = ['Последние действия:']
    for item in rows:
        created = item.created_at.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') if item.created_at else '-'
        payload = item.payload_json or {}
        mode = payload.get('mode') if isinstance(payload, dict) else None
        title = MODE_TITLES.get(mode, item.action_type) if mode else item.action_type
        lines.append(f'• {created} — {title}')

    await callback.message.edit_text('\n'.join(lines), reply_markup=history_keyboard())
    await callback.answer()
