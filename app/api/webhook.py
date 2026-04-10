from fastapi import APIRouter, Header, HTTPException, Request, status
from aiogram.types import Update

from app.config import get_settings

router = APIRouter(tags=['telegram'])
settings = get_settings()


@router.post(settings.webhook_path)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    if settings.telegram_mode != 'webhook':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Webhook mode is disabled')

    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid secret token')

    app_state = request.app.state
    bot = app_state.bot
    dp = app_state.dp

    update_data = await request.json()
    update = Update.model_validate(update_data)
    await dp.feed_update(bot, update)
    return {'ok': True}
