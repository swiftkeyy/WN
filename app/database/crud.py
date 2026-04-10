from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import PromptTemplate, Task, User, UserHistory


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    language_code: str | None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        language_code=language_code,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_profile(
    session: AsyncSession,
    user: User,
    username: str | None,
    first_name: str | None,
    language_code: str | None,
) -> User:
    user.username = username
    user.first_name = first_name
    user.language_code = language_code
    await session.commit()
    await session.refresh(user)
    return user


async def create_task(
    session: AsyncSession,
    *,
    user_id: int,
    task_type: str,
    input_text: str | None = None,
    input_file_path: str | None = None,
    output_file_path: str | None = None,
    status: str = 'pending',
    provider: str | None = None,
    error_message: str | None = None,
) -> Task:
    task = Task(
        user_id=user_id,
        task_type=task_type,
        input_text=input_text,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        status=status,
        provider=provider,
        error_message=error_message,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task_status(
    session,
    task_id: int,
    status: str,
    output_file_path: str | None = None,
    error_message: str | None = None,
):


async def create_history_entry(
    session: AsyncSession,
    *,
    user_id: int,
    action_type: str,
    payload_json: dict[str, Any] | list[Any] | None = None,
) -> UserHistory:
    entry = UserHistory(user_id=user_id, action_type=action_type, payload_json=payload_json)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def list_user_history(session: AsyncSession, user_id: int, limit: int = 10) -> list[UserHistory]:
    result = await session.execute(
        select(UserHistory)
        .where(UserHistory.user_id == user_id)
        .order_by(UserHistory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_active_templates(session: AsyncSession) -> list[PromptTemplate]:
    result = await session.execute(
        select(PromptTemplate)
        .where(PromptTemplate.is_active.is_(True))
        .order_by(PromptTemplate.category.asc(), PromptTemplate.title.asc())
    )
    return list(result.scalars().all())


async def get_template_by_key(session: AsyncSession, key: str) -> PromptTemplate | None:
    result = await session.execute(select(PromptTemplate).where(PromptTemplate.key == key))
    return result.scalar_one_or_none()


async def upsert_prompt_template(
    session: AsyncSession,
    *,
    key: str,
    title: str,
    category: str,
    prompt_text: str,
    is_active: bool,
) -> PromptTemplate:
    existing = await get_template_by_key(session, key)
    if existing:
        existing.title = title
        existing.category = category
        existing.prompt_text = prompt_text
        existing.is_active = is_active
        await session.commit()
        await session.refresh(existing)
        return existing

    template = PromptTemplate(
        key=key,
        title=title,
        category=category,
        prompt_text=prompt_text,
        is_active=is_active,
    )
    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template
