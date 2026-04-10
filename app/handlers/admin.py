from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.database.session import AsyncSessionLocal
from app.keyboards.admin_menu import (
    build_admin_menu_keyboard,
    build_admin_template_toggle_keyboard,
    build_admin_templates_keyboard,
)
from app.services.admin_service import AdminService

router = Router()
settings = get_settings()
admin_service = AdminService()


def _admin_ids() -> set[int]:
    raw = str(getattr(settings, "admin_telegram_ids", "") or "").strip()

    result: set[int] = set()
    for part in raw.split(","):
        part = part.strip().replace(" ", "")
        if not part:
            continue
        try:
            result.add(int(part))
        except ValueError:
            continue
    return result


def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return int(user_id) in _admin_ids()


def admin_denied_text(user_id: int | None) -> str:
    return (
        "У тебя нет доступа к админке.\n\n"
        f"Твой Telegram ID: {user_id}\n"
        f"ADMIN_TELEGRAM_IDS: {getattr(settings, 'admin_telegram_ids', '')}"
    )


@router.message(Command("admin"))
async def admin_entry(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None

    if not is_admin(user_id):
        await message.answer(admin_denied_text(user_id))
        return

    await message.answer(
        "Админка бота:",
        reply_markup=build_admin_menu_keyboard(),
    )


@router.callback_query(F.data == "admin:root")
async def admin_root(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "Админка бота:",
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        stats = await admin_service.get_stats(session)

    text = (
        "📊 Статистика\n\n"
        f"Пользователи: {stats['users_count']}\n"
        f"Задачи: {stats['tasks_count']}\n"
        f"История: {stats['history_count']}\n"
        f"Шаблоны: {stats['templates_count']}\n"
        f"Ошибки: {stats['failed_tasks']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        items = await admin_service.get_recent_users(session)

    if not items:
        text = "Пользователей пока нет."
    else:
        lines = ["👤 Последние пользователи:\n"]
        for item in items:
            lines.append(
                f"{item.id}. tg={item.telegram_id} | @{item.username or '-'} | {item.first_name or '-'}"
            )
        text = "\n".join(lines[:30])

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:tasks")
async def admin_tasks(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        items = await admin_service.get_recent_tasks(session)

    if not items:
        text = "Задач пока нет."
    else:
        lines = ["🧾 Последние задачи:\n"]
        for item in items:
            lines.append(
                f"{item.id}. user={item.user_id} | {item.task_type} | {item.status} | {item.provider or '-'}"
            )
        text = "\n".join(lines[:30])

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:errors")
async def admin_errors(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        items = await admin_service.get_failed_tasks(session)

    if not items:
        text = "Ошибок пока нет."
    else:
        lines = ["⚠️ Последние ошибки:\n"]
        for item in items:
            lines.append(
                f"{item.id}. {item.task_type} | {item.error_message or 'без текста ошибки'}"
            )
        text = "\n\n".join(lines[:15])

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:history")
async def admin_history(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        items = await admin_service.get_recent_history(session)

    if not items:
        text = "История пока пуста."
    else:
        lines = ["🕘 Последняя история:\n"]
        for item in items:
            lines.append(f"{item.id}. user={item.user_id} | {item.action_type}")
        text = "\n".join(lines[:30])

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:templates")
async def admin_templates(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        items = await admin_service.get_templates(session)

    await callback.message.edit_text(
        "🧩 Шаблоны:",
        reply_markup=build_admin_templates_keyboard(items),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_tpl:"))
async def admin_template_view(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    template_id = int(callback.data.split(":", 1)[1])

    async with AsyncSessionLocal() as session:
        item = await admin_service.get_template_by_id(session, template_id)

    if item is None:
        await callback.answer("Шаблон не найден", show_alert=True)
        return

    text = (
        f"🧩 {item.title}\n\n"
        f"Key: {item.key}\n"
        f"Категория: {item.category}\n"
        f"Активен: {'да' if item.is_active else 'нет'}\n\n"
        f"{item.prompt_text[:1500]}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_template_toggle_keyboard(item.id, item.is_active),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_tpl_toggle:"))
async def admin_template_toggle(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None

    if not is_admin(user_id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    _, template_id, action = callback.data.split(":")
    template_id = int(template_id)
    is_active = action == "on"

    async with AsyncSessionLocal() as session:
        item = await admin_service.set_template_active(session, template_id, is_active)

    if item is None:
        await callback.answer("Шаблон не найден", show_alert=True)
        return

    text = (
        f"🧩 {item.title}\n\n"
        f"Key: {item.key}\n"
        f"Категория: {item.category}\n"
        f"Активен: {'да' if item.is_active else 'нет'}\n\n"
        f"{item.prompt_text[:1500]}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=build_admin_template_toggle_keyboard(item.id, item.is_active),
    )
    await callback.answer("Готово")
