from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PromptTemplate, Task, User, UserHistory


class AdminService:
    async def get_stats(self, session: AsyncSession) -> dict:
        users_count = await session.scalar(select(func.count()).select_from(User))
        tasks_count = await session.scalar(select(func.count()).select_from(Task))
        history_count = await session.scalar(select(func.count()).select_from(UserHistory))
        templates_count = await session.scalar(select(func.count()).select_from(PromptTemplate))
        failed_tasks = await session.scalar(
            select(func.count()).select_from(Task).where(Task.status == "failed")
        )

        return {
            "users_count": users_count or 0,
            "tasks_count": tasks_count or 0,
            "history_count": history_count or 0,
            "templates_count": templates_count or 0,
            "failed_tasks": failed_tasks or 0,
        }

    async def get_recent_users(self, session: AsyncSession, limit: int = 20):
        result = await session.execute(
            select(User).order_by(desc(User.created_at)).limit(limit)
        )
        return result.scalars().all()

    async def get_recent_tasks(self, session: AsyncSession, limit: int = 20):
        result = await session.execute(
            select(Task).order_by(desc(Task.created_at)).limit(limit)
        )
        return result.scalars().all()

    async def get_failed_tasks(self, session: AsyncSession, limit: int = 20):
        result = await session.execute(
            select(Task)
            .where(Task.status == "failed")
            .order_by(desc(Task.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_history(self, session: AsyncSession, limit: int = 20):
        result = await session.execute(
            select(UserHistory).order_by(desc(UserHistory.created_at)).limit(limit)
        )
        return result.scalars().all()

    async def get_templates(self, session: AsyncSession, limit: int = 20):
        result = await session.execute(
            select(PromptTemplate).order_by(PromptTemplate.category, PromptTemplate.title).limit(limit)
        )
        return result.scalars().all()

    async def get_template_by_id(self, session: AsyncSession, template_id: int):
        return await session.get(PromptTemplate, template_id)

    async def set_template_active(
        self,
        session: AsyncSession,
        template_id: int,
        is_active: bool,
    ):
        item = await session.get(PromptTemplate, template_id)
        if item is None:
            return None

        item.is_active = is_active
        await session.commit()
        await session.refresh(item)
        return item
