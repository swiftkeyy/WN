from datetime import timezone

from aiogram import F, Router
from aiogram.types import Message

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import MAIN_MENU
from app.services.history_service import HistoryService
from app.services.user_service import UserService

router = Router()
history_service = HistoryService()
user_service = UserService()


@router.message(F.text == 'История')
async def history_handler(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        rows = await history_service.list_recent(session, user.id)

    if not rows:
        await message.answer('История пока пустая.', reply_markup=MAIN_MENU)
        return

    lines = ['Последние действия:']
    for item in rows:
        created = item.created_at.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC') if item.created_at else '-'
        lines.append(f'• {created} — {item.action_type}')
    await message.answer('\n'.join(lines), reply_markup=MAIN_MENU)
