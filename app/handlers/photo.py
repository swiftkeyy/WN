from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message, ReplyKeyboardRemove

from app.database import crud
from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.integrations.remove_bg_client import RemoveBgClient
from app.keyboards.main_menu import build_main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.image_workflow_service import ImageWorkflowService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, TaskStatuses, TaskTypes
from app.utils.files import save_telegram_photo

router = Router()
remove_bg_client = RemoveBgClient()
image_workflow_service = ImageWorkflowService()
user_service = UserService()
history_service = HistoryService()


MODE_TITLES = {
    "remove_bg": "Удалить фон",
    "avatar": "Сделать аватар",
    "poster": "Сделать постер",
    "stickers": "Сделать стикеры",
    "product": "Оформить товар",
}


async def _set_mode(callback: CallbackQuery, state: FSMContext, mode: str, text: str) -> None:
    await state.clear()
    await state.set_state(BotStates.waiting_for_photo)
    await state.update_data(mode=mode)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=build_main_menu_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "menu:remove_bg")
async def remove_bg_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _set_mode(
        callback,
        state,
        mode="remove_bg",
        text="Режим «Удалить фон» включён.\n\nПришли фото, и я верну PNG без фона.",
    )


@router.callback_query(F.data == "menu:avatar")
async def avatar_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _set_mode(
        callback,
        state,
        mode="avatar",
        text="Режим «Аватар» включён.\n\nПришли фото. При желании после этого напиши короткое пожелание по стилю.",
    )


@router.callback_query(F.data == "menu:poster")
async def poster_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _set_mode(
        callback,
        state,
        mode="poster",
        text="Режим «Постер» включён.\n\nПришли фото. При желании после этого напиши короткую идею постера.",
    )


@router.callback_query(F.data == "menu:stickers")
async def stickers_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _set_mode(
        callback,
        state,
        mode="stickers",
        text="Режим «Стикеры» включён.\n\nПришли фото. При желании после этого напиши настроение: мемно, мило, аниме и т.д.",
    )


@router.callback_query(F.data == "menu:product")
async def product_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _set_mode(
        callback,
        state,
        mode="product",
        text="Режим «Оформить товар» включён.\n\nПришли фото товара. При желании после этого напиши стиль оформления.",
    )


@router.message(F.photo, BotStates.waiting_for_photo)
async def handle_photo_in_selected_mode(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "remove_bg")
    user_text = data.get("user_text", "")

    status_message = await message.answer(
        f"Фото получено. Выполняю режим «{MODE_TITLES.get(mode, mode)}»...",
        reply_markup=ReplyKeyboardRemove(),
    )

    photo = message.photo[-1]
    input_path = await save_telegram_photo(message.bot, photo, prefix=mode)

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        task = await crud.create_task(
            session,
            user_id=user.id,
            task_type=TaskTypes.REMOVE_BG if mode == "remove_bg" else mode,
            input_text=user_text or None,
            input_file_path=input_path,
            status=TaskStatuses.PROCESSING,
            provider="system",
        )

        await history_service.log(
            session,
            user_id=user.id,
            action_type=f"{HistoryActions.TEXT_ASSISTANT}_{mode}",
            payload_json={"mode": mode, "input_path": input_path},
        )

        try:
            if mode == "remove_bg":
                output_path = await remove_bg_client.remove_background(input_path)
                provider_name = "remove.bg"
            else:
                result = await image_workflow_service.process_image(
                    mode=mode,
                    input_path=input_path,
                    user_text=user_text or "",
                )
                output_path = result.output_path
                provider_name = result.provider

            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.DONE,
                output_file_path=output_path,
                provider=provider_name,
            )

        except Exception as exc:  # noqa: BLE001
            await crud.update_task_status(
                session,
                task.id,
                status=TaskStatuses.FAILED,
                error_message=str(exc),
            )
            await status_message.edit_text(
                f"Не удалось выполнить режим «{MODE_TITLES.get(mode, mode)}».\n\n{exc}",
                reply_markup=build_main_menu_keyboard(),
            )
            return

    file_bytes = Path(output_path).read_bytes()
    tg_file = BufferedInputFile(file=file_bytes, filename=Path(output_path).name)

    caption = (
        f"Готово. Режим: «{MODE_TITLES.get(mode, mode)}»."
        if mode == "remove_bg"
        else f"Готово. Результат по режиму «{MODE_TITLES.get(mode, mode)}»."
    )

    await message.answer_document(
        tg_file,
        caption=caption,
    )

    await status_message.delete()

    await message.answer(
        "Что делаем дальше?",
        reply_markup=build_main_menu_keyboard(),
    )

    await state.clear()


@router.message(F.photo)
async def generic_photo_fallback(message: Message) -> None:
    await message.answer(
        "Сначала выбери режим через inline-меню, потом пришли фото.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Выбери действие:",
        reply_markup=build_main_menu_keyboard(),
    )
