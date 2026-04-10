import logging
import os

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import MAIN_MENU
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions

router = Router()
user_service = UserService()
history_service = HistoryService()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    logger.warning(
        "START handler called | pid=%s | user_id=%s | update_id=%s | text=%s",
        os.getpid(),
        message.from_user.id if message.from_user else None,
        message.message_id,
        message.text,
    )

    await state.clear()

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.START,
            payload_json={'source': '/start'},
        )

    text = (
        'Привет. Я AI Photo Bot.\n\n'
        'Что умею сейчас:\n'
        '• удалить фон через remove.bg\n'
        '• улучшить сырой промпт через Gemini\n'
        '• применить трендовый шаблон\n'
        '• помочь с идеей, caption и визуальным направлением\n\n'
        'Нажми кнопку ниже или просто отправь фото / текст.'
    )
    await message.answer(text, reply_markup=MAIN_MENU)
