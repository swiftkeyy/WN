from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Удалить фон'), KeyboardButton(text='Улучшить промпт')],
        [KeyboardButton(text='Трендовые шаблоны'), KeyboardButton(text='История')],
        [KeyboardButton(text='Помощь')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие или отправьте сообщение',
)
