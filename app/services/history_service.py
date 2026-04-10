from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import crud
from app.database.models import UserHistory


class HistoryService:
    """Service for persisting and reading user history."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def log(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        action_type: str,
        payload_json: dict[str, Any] | list[Any] | None = None,
    ) -> UserHistory:
        return await crud.create_history_entry(
            session,
            user_id=user_id,
            action_type=action_type,
            payload_json=payload_json,
        )

    async def list_recent(self, session: AsyncSession, user_id: int) -> list[UserHistory]:
        return await crud.list_user_history(session, user_id=user_id, limit=self.settings.max_history_items)
