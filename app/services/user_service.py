from __future__ import annotations

from aiogram.types import User as TgUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import User


class UserService:
    async def get_or_create_user(
        self,
        session: AsyncSession,
        telegram_user: TgUser | None,
    ) -> User:
        if telegram_user is None:
            raise ValueError("telegram_user is required")

        existing = await crud.get_user_by_telegram_id(session, telegram_user.id)

        if existing is None:
            return await crud.create_user(
                session=session,
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                language_code=telegram_user.language_code,
            )

        updated = await crud.update_user_profile(
            session=session,
            user_id=existing.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            language_code=telegram_user.language_code,
        )
        if updated is None:
            raise RuntimeError("failed to update existing user")
        return updated
