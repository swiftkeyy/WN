from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from app.config import get_settings
from app.handlers.help import router as help_router
from app.handlers.history import router as history_router
from app.handlers.photo import router as photo_router
from app.handlers.start import router as start_router
from app.handlers.templates import router as templates_router
from app.handlers.text import router as text_router

logger = logging.getLogger(__name__)
settings = get_settings()



def create_bot() -> Bot:
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command='start', description='Открыть меню'),
            BotCommand(command='menu', description='Показать меню'),
            BotCommand(command='help', description='Помощь'),
        ]
    )



def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(history_router)
    dp.include_router(templates_router)
    dp.include_router(photo_router)
    dp.include_router(text_router)
    return dp


async def setup_webhook(bot: Bot) -> None:
    await bot.set_webhook(
        url=settings.webhook_full_url,
        secret_token=settings.telegram_webhook_secret,
        drop_pending_updates=True,
    )
    logger.info('Telegram webhook configured: %s', settings.webhook_full_url)


async def delete_webhook(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
