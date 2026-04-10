from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud
from app.database.models import UserHistory


class HistoryService:
    async def log(
        self,
        session: AsyncSession,
        user_id: int,
        action_type: str,
        payload_json: dict | list | None = None,
    ) -> UserHistory:
        return await crud.create_history_entry(
            session=session,
            user_id=user_id,
            action_type=action_type,
            payload_json=payload_json,
        )

    async def get_recent(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> list[UserHistory]:
        items = await crud.get_user_history(
            session=session,
            user_id=user_id,
            limit=limit,
        )
        return list(items)
