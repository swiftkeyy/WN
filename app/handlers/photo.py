from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message, ReplyKeyboardRemove

from app.database import crud
from app.database.session import AsyncSessionLocal
from app.handlers.states import BotStates
from app.integrations.remove_bg_client import RemoveBgClient
from app.keyboards.main_menu import (
    build_main_menu_keyboard,
    mode_title,
    photo_request_keyboard,
)
from app.services.history_service import HistoryService
from app.services.image_workflow_service import ImageWorkflowService
from app.services.user_service import UserService
from app.utils.constants import HistoryActions, TaskStatuses, TaskTypes

router = Router()
remove_bg_client = RemoveBgClient()
image_workflow_service = ImageWorkflowService()
user_service = UserService()
history_service = HistoryService()


async def save_telegram_photo(bot, photo, prefix: str) -> str:
    file = await bot.get_file(photo.file_id)
    file_path = f"./data/media/input/{prefix}_{photo.file_id}.jpg"
    Path("./data/media/input").mkdir(parents=True, exist_ok=True)
    await bot.download_file(file.file_path, destination=file_path)
    return file_path


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
) -> None:
    if not callback.message:
        await callback.answer()
        return

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc).lower():
            await callback.answer("Уже открыто")
            return
        raise

    await callback.answer()


async def open_mode(
    callback: CallbackQuery,
    state: FSMContext,
    mode: str,
    text: str,
) -> None:
    await state.clear()
    await state.set_state(BotStates.waiting_for_photo)
    await state.update_data(mode=mode, user_text="", style_key="")

    await safe_edit(
        callback,
        text=text,
        reply_markup=photo_request_keyboard(),
    )


@router.callback_query(F.data == "menu:root")
async def back_to_root_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit(
        callback,
        text="Выбери действие:",
        reply_markup=build_main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu:remove_bg")
async def remove_bg_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await open_mode(
        callback,
        state,
        mode="remove_bg",
        text="Режим «Удалить фон» включён.\n\nПришли фото, и я верну PNG без фона.",
    )


@router.callback_query(F.data == "menu:avatar")
async def avatar_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await open_mode(
        callback,
        state,
        mode="avatar",
        text="Режим «Аватар» включён.\n\nПришли фото. Потом можешь отдельно написать стиль: old money, cyberpunk, anime и т.д.",
    )


@router.callback_query(F.data == "menu:poster")
async def poster_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await open_mode(
        callback,
        state,
        mode="poster",
        text="Режим «Постер» включён.\n\nПришли фото. Потом можешь отдельно написать идею постера.",
    )


@router.callback_query(F.data == "menu:stickers")
async def stickers_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await open_mode(
        callback,
        state,
        mode="stickers",
        text="Режим «Стикеры» включён.\n\nПришли фото. Потом можешь отдельно написать настроение: мемно, мило, аниме и т.д.",
    )


@router.callback_query(F.data == "menu:product")
async def product_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await open_mode(
        callback,
        state,
        mode="product",
        text="Режим «Оформить товар» включён.\n\nПришли фото товара. Потом можешь отдельно написать стиль оформления.",
    )


@router.message(F.photo, BotStates.waiting_for_photo)
async def handle_photo_in_selected_mode(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("mode", "remove_bg")
    user_text = data.get("user_text", "")
    style_key = data.get("style_key", "")

    status_message = await message.answer(
        f"Фото получено. Выполняю режим «{mode_title(mode)}»...",
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
            payload_json={
                "mode": mode,
                "input_path": input_path,
                "style_key": style_key,
                "user_text": user_text,
            },
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
                    style_key=style_key or None,
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
                f"Не удалось выполнить режим «{mode_title(mode)}».\n\n{exc}",
                reply_markup=build_main_menu_keyboard(),
            )
            await state.clear()
            return

    file_bytes = Path(output_path).read_bytes()
    tg_file = BufferedInputFile(file=file_bytes, filename=Path(output_path).name)

    await message.answer_document(
        tg_file,
        caption=f"Готово. Режим: «{mode_title(mode)}».",
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
        "Сначала выбери режим через меню, потом пришли фото.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Выбери действие:",
        reply_markup=build_main_menu_keyboard(),
    )
