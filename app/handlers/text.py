from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(Command('menu'))
async def menu_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('Выбери, что сделать с фото:', reply_markup=main_menu_keyboard())


@router.message(F.text & ~F.text.startswith('/'))
async def free_text_router_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state:
        await message.answer(
            'Сейчас я жду от тебя фото для выбранного режима.\n'
            'Можно отправить фотографию с подписью-пожеланием.',
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        'Я работаю через кнопки и фото. Нажми /start и выбери нужный режим.',
        reply_markup=main_menu_keyboard(),
    )
