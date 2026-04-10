from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import User


class UserService:
    """User management service."""

    async def get_or_create_user(self, session: AsyncSession, tg_user: TgUser) -> User:
        user = await crud.get_user_by_telegram_id(session, tg_user.id)
        if user is None:
            return await crud.create_user(
                session,
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                language_code=tg_user.language_code,
            )
        return await crud.update_user_profile(
            session,
            user,
            username=tg_user.username,
            first_name=tg_user.first_name,
            language_code=tg_user.language_code,
        )
