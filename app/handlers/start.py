from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions

router = Router()
user_service = UserService()
history_service = HistoryService()


WELCOME_TEXT = (
    'Привет. Я бот для обработки фото.\n\n'
    'Я не выдаю промпты пользователю, а стараюсь сам сделать готовый результат.\n\n'
    'Что можно сделать сейчас:\n'
    '• удалить фон\n'
    '• сделать аватар\n'
    '• сделать постер\n'
    '• сделать набор стикеров\n'
    '• оформить товарное фото\n\n'
    'Выбери режим кнопками ниже.'
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.START,
            payload_json={'source': '/start'},
        )
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())
