import asyncio

from app.bot import create_bot, create_dispatcher, delete_webhook, set_bot_commands
from app.utils.files import ensure_media_dirs
from app.utils.logging import setup_logging


async def main() -> None:
    setup_logging()
    ensure_media_dirs()
    bot = create_bot()
    dp = create_dispatcher()
    await delete_webhook(bot)
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
