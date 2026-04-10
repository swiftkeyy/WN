import asyncio
import logging

from aiogram.exceptions import TelegramUnauthorizedError

from app.bot import create_bot, create_dispatcher, delete_webhook, set_bot_commands
from app.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.template_service import TemplateService
from app.utils.files import ensure_media_dirs
from app.utils.logging import setup_logging

settings = get_settings()
template_service = TemplateService()
logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    ensure_media_dirs()

    async with AsyncSessionLocal() as session:
        await template_service.seed_from_file(session)

    bot = create_bot()
    dp = create_dispatcher()

    try:
        try:
            await set_bot_commands(bot)
        except TelegramUnauthorizedError:
            logger.error("Invalid TELEGRAM_BOT_TOKEN")
            return
        except Exception as exc:
            logger.warning("set_my_commands skipped: %s", exc)

        try:
            await delete_webhook(bot)
        except Exception as exc:
            logger.warning("delete_webhook skipped: %s", exc)

        logger.info("Bot started in polling mode")
        await dp.start_polling(bot, skip_updates=True)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
