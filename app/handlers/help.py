from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.ai.gemini_client import GeminiClient
from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import history_keyboard, main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions

router = Router()
user_service = UserService()
history_service = HistoryService()
gemini_client = GeminiClient()


@router.message(Command('help'))
async def help_command(message: Message) -> None:
    text = await gemini_client.generate_help_text()
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await history_service.log(session, user_id=user.id, action_type=HistoryActions.HELP, payload_json={'source': '/help'})
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == 'menu:help')
async def help_callback(callback: CallbackQuery) -> None:
    text = await gemini_client.generate_help_text()
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, callback.from_user)
        await history_service.log(session, user_id=user.id, action_type=HistoryActions.HELP, payload_json={'source': 'inline'})
    await callback.message.edit_text(text, reply_markup=history_keyboard())
    await callback.answer()
