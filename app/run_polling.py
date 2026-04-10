import asyncio
import logging

from aiogram.exceptions import TelegramUnauthorizedError

from app.bot import create_bot, create_dispatcher, delete_webhook, set_bot_commands
from app.database.session import AsyncSessionLocal
from app.services.template_service import TemplateService
from app.utils.files import ensure_media_dirs
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)
template_service = TemplateService()


async def main() -> None:
    setup_logging()
    ensure_media_dirs()

    async with AsyncSessionLocal() as session:
        await template_service.seed_from_file(session)

    bot = create_bot()
    dp = create_dispatcher()

    try:
        try:
            await delete_webhook(bot)
            await set_bot_commands(bot)
        except TelegramUnauthorizedError:
            logger.error('Неверный TELEGRAM_BOT_TOKEN')
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning('Пропускаю часть Telegram init: %s', exc)

        logger.info('Бот запущен в режиме polling')
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
