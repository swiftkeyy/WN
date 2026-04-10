from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin:stats")
    builder.button(text="👤 Пользователи", callback_data="admin:users")
    builder.button(text="🧾 Задачи", callback_data="admin:tasks")
    builder.button(text="🕘 История", callback_data="admin:history")
    builder.button(text="🧩 Шаблоны", callback_data="admin:templates")
    builder.button(text="⚠️ Ошибки", callback_data="admin:errors")
    builder.button(text="🔙 В меню", callback_data="menu:root")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def build_admin_templates_keyboard(items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items[:20]:
        icon = "✅" if item.is_active else "❌"
        builder.button(
            text=f"{icon} {item.title}",
            callback_data=f"admin_tpl:{item.id}",
        )

    builder.button(text="🔙 В админку", callback_data="admin:root")
    builder.adjust(1)
    return builder.as_markup()


def build_admin_template_toggle_keyboard(template_id: int, is_active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_active:
        builder.button(text="🚫 Отключить", callback_data=f"admin_tpl_toggle:{template_id}:off")
    else:
        builder.button(text="✅ Включить", callback_data=f"admin_tpl_toggle:{template_id}:on")

    builder.button(text="🔙 К шаблонам", callback_data="admin:templates")
    builder.adjust(1)
    return builder.as_markup()
