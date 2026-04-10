from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from app.bot import create_bot, create_dispatcher, delete_webhook, set_bot_commands, setup_webhook
from app.config import get_settings
from app.database.session import AsyncSessionLocal
from app.services.template_service import TemplateService
from app.utils.files import ensure_media_dirs
from app.utils.logging import setup_logging

settings = get_settings()
template_service = TemplateService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    ensure_media_dirs()

    bot = create_bot()
    dp = create_dispatcher()
    app.state.bot = bot
    app.state.dp = dp

    async with AsyncSessionLocal() as session:
        await template_service.seed_from_file(session)

    await set_bot_commands(bot)

    if settings.telegram_mode == 'webhook':
        await setup_webhook(bot)
    else:
        await delete_webhook(bot)

    yield

    await bot.session.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router, prefix='/api')
app.include_router(webhook_router)
