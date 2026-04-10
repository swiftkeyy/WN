from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import MAIN_MENU
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions

router = Router()
user_service = UserService()
history_service = HistoryService()


HELP_TEXT = (
    'Доступные сценарии:\n\n'
    '1) Удалить фон — нажми кнопку и пришли фото.\n'
    '2) Улучшить промпт — нажми кнопку и пришли сырой запрос.\n'
    '3) Трендовые шаблоны — выбери категорию и шаблон.\n'
    '4) Свободный текст — я попробую понять, нужен ли тебе caption, poster idea, avatar makeover, product photo или sticker pack prompt.\n\n'
    'Поддерживаемая архитектура уже готова к добавлению отдельного image generation provider adapter.'
)


@router.message(Command('help'))
@router.message(F.text == 'Помощь')
async def help_handler(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.HELP,
            payload_json={'source': 'help'},
        )
    await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)
