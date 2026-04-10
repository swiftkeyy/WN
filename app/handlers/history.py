from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.database.session import AsyncSessionLocal
from app.keyboards.main_menu import build_main_menu_keyboard
from app.services.history_service import HistoryService
from app.services.user_service import UserService

router = Router()
history_service = HistoryService()
user_service = UserService()


def _format_history_item(action_type: str, created_at, payload_json) -> str:
    created = created_at.strftime("%d.%m %H:%M") if created_at else "—"
    payload = f" | {payload_json}" if payload_json else ""
    return f"• {created} — {action_type}{payload}"


@router.message(F.text == "История")
async def history_message_compat(message: Message) -> None:
    await show_history_message(message)


@router.callback_query(F.data == "menu:history")
async def history_callback(callback: CallbackQuery) -> None:
    if not callback.message or not callback.from_user:
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, callback.from_user)
        items = await history_service.get_recent(session, user.id)

    if not items:
        text = "История пока пустая."
    else:
        lines = ["Последние действия:\n"]
        for item in items:
            lines.append(
                _format_history_item(
                    action_type=item.action_type,
                    created_at=item.created_at,
                    payload_json=item.payload_json,
                )
            )
        text = "\n".join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=build_main_menu_keyboard(),
    )
    await callback.answer()


async def show_history_message(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        user = await user_service.get_or_create_user(session, message.from_user)
        items = await history_service.get_recent(session, user.id)

    if not items:
        text = "История пока пустая."
    else:
        lines = ["Последние действия:\n"]
        for item in items:
            lines.append(
                _format_history_item(
                    action_type=item.action_type,
                    created_at=item.created_at,
                    payload_json=item.payload_json,
                )
            )
        text = "\n".join(lines)

    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        "Что делаем дальше?",
        reply_markup=build_main_menu_keyboard(),
    )
