from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from app.ai.gemini_client import GeminiClient
from app.database import crud
from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.integrations.remove_bg_client import RemoveBgClient
from app.keyboards.main_menu import MAIN_MENU
from app.services.history_service import HistoryService
from app.services.template_service import TemplateService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, TaskStatuses, TaskTypes
from app.utils.files import save_telegram_photo

router = Router()
remove_bg_client = RemoveBgClient()
gemini_client = GeminiClient()
template_service = TemplateService()
user_service = UserService()
history_service = HistoryService()


@router.message(F.text == 'Удалить фон')
async def remove_bg_entrypoint(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.waiting_for_remove_bg_photo)
    await message.answer('Пришли фото. Я удалю фон и верну PNG с прозрачностью.', reply_markup=MAIN_MENU)


@router.message(F.photo, BotStates.waiting_for_remove_bg_photo)
async def handle_remove_bg_photo(message: Message, state: FSMContext) -> None:
    status_message = await message.answer('Фото получено. Удаляю фон...')
    photo = message.photo[-1]
    input_path = await save_telegram_photo(message.bot, photo, prefix='remove_bg')

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        task = await crud.create_task(
            session,
            user_id=user.id,
            task_type=TaskTypes.REMOVE_BG,
            input_file_path=input_path,
            status=TaskStatuses.PROCESSING,
            provider='remove.bg',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.REMOVE_BG_REQUESTED,
            payload_json={'input_path': input_path},
        )

        try:
            output_path = await remove_bg_client.remove_background(input_path)
            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.DONE,
                output_file_path=output_path,
            )
            await history_service.log(
                session,
                user_id=user.id,
                action_type=HistoryActions.REMOVE_BG_DONE,
                payload_json={'output_path': output_path},
            )
        except Exception as exc:  # noqa: BLE001
            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.FAILED,
                error_message=str(exc),
            )
            await status_message.edit_text(f'Не удалось удалить фон: {exc}')
            await state.clear()
            return

    file_bytes = Path(output_path).read_bytes()
    tg_file = BufferedInputFile(file=file_bytes, filename=Path(output_path).name)
    await message.answer_document(
        tg_file,
        caption='Готово. Ниже PNG без фона.',
        reply_markup=MAIN_MENU,
    )
    await status_message.delete()
    await state.clear()


@router.message(F.photo, BotStates.waiting_for_template_input)
async def handle_template_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    input_path = await save_telegram_photo(message.bot, photo, prefix='template')
    data = await state.get_data()
    template_key = data.get('template_key', 'unknown_template')

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        template = await template_service.get_by_key(session, template_key)
        final_prompt = await gemini_client.build_template_prompt(
            template_key=template_key,
            user_input=f'User uploaded photo at path: {input_path}',
            base_template=template.prompt_text if template else None,
        )
        await crud.create_task(
            session,
            user_id=user.id,
            task_type=TaskTypes.TEMPLATE_APPLY,
            input_file_path=input_path,
            input_text=template_key,
            status=TaskStatuses.DONE,
            provider='gemini',
        )
        await history_service.log(
            session,
            user_id=user.id,
            action_type=HistoryActions.TEMPLATE_APPLIED,
            payload_json={'template_key': template_key, 'input_file_path': input_path},
        )

    await message.answer(
        f'Финальный prompt для шаблона {template_key}:\n\n{final_prompt}\n\nТеперь этот prompt можно отправить в image generation provider.',
        reply_markup=MAIN_MENU,
    )
    await state.clear()


@router.message(F.photo)
async def generic_photo_fallback(message: Message) -> None:
    await message.answer(
        'Фото получено. Чтобы удалить фон, сначала нажми «Удалить фон».\n'
        'Чтобы применить трендовый шаблон, нажми «Трендовые шаблоны» и выбери шаблон.',
        reply_markup=MAIN_MENU,
    )
