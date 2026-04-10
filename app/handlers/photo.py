from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from app.database import crud
from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.keyboards.main_menu import main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.image_workflow_service import ImageWorkflowService
from app.services.user_service import UserService
from app.utils.constants import BotModes, HistoryActions, MODE_TITLES, TaskStatuses, TaskTypes
from app.utils.files import save_telegram_photo

router = Router()
workflow_service = ImageWorkflowService()
user_service = UserService()
history_service = HistoryService()


MODE_TO_TASK_TYPE = {
    BotModes.REMOVE_BG: TaskTypes.REMOVE_BG,
    BotModes.AVATAR: TaskTypes.AVATAR,
    BotModes.POSTER: TaskTypes.POSTER,
    BotModes.STICKERS: TaskTypes.STICKERS,
    BotModes.PRODUCT: TaskTypes.PRODUCT,
}


@router.message(BotStates.waiting_for_photo, F.photo)
async def handle_mode_photo(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    mode = state_data.get('mode')
    style_key = state_data.get('style_key')
    user_text = (message.caption or '').strip() or None

    if not mode:
        await message.answer('Сначала выбери режим кнопками через /start.', reply_markup=main_menu_keyboard())
        await state.clear()
        return

    status_message = await message.answer('Фото получил. Обрабатываю...')
    photo = message.photo[-1]
    input_path = await save_telegram_photo(message.bot, photo, prefix=mode)

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        task = await crud.create_task(
            session,
            user_id=user.id,
            task_type=MODE_TO_TASK_TYPE[mode],
            input_text=user_text,
            input_file_path=input_path,
            status=TaskStatuses.PROCESSING,
            provider='workflow',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.IMAGE_TASK_REQUESTED,
            payload_json={'mode': mode, 'style_key': style_key},
        )

        try:
            output_path = await workflow_service.process(
                mode=mode,
                input_path=input_path,
                user_text=user_text,
                style_key=style_key,
            )
            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.DONE,
                output_file_path=output_path,
            )
            await history_service.log(
                session,
                user_id=user.id,
                action_type=HistoryActions.IMAGE_TASK_DONE,
                payload_json={'mode': mode, 'style_key': style_key, 'output_path': output_path},
            )
        except Exception as exc:  # noqa: BLE001
            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.FAILED,
                error_message=str(exc),
            )
            await history_service.log(
                session,
                user_id=user.id,
                action_type=HistoryActions.IMAGE_TASK_FAILED,
                payload_json={'mode': mode, 'style_key': style_key, 'error': str(exc)},
            )
            await status_message.edit_text(
                f'Не удалось выполнить режим «{MODE_TITLES.get(mode, mode)}».\n\n{exc}',
                reply_markup=main_menu_keyboard(),
            )
            await state.clear()
            return

    file_bytes = Path(output_path).read_bytes()
    filename = Path(output_path).name
    tg_file = BufferedInputFile(file=file_bytes, filename=filename)

    if mode == BotModes.REMOVE_BG:
        await message.answer_document(
            tg_file,
            caption='Готово. Ниже PNG без фона.',
        )
    else:
        await message.answer_photo(
            tg_file,
            caption=f'Готово. Режим: {MODE_TITLES.get(mode, mode)}.',
        )

    await status_message.delete()
    await message.answer('Что делаем дальше?', reply_markup=main_menu_keyboard())
    await state.clear()


@router.message(F.photo)
async def generic_photo_fallback(message: Message) -> None:
    await message.answer(
        'Сначала выбери режим кнопками. Нажми /start и выбери, что нужно сделать с фото.',
        reply_markup=main_menu_keyboard(),
    )
