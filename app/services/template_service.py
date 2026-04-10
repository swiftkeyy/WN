from __future__ import annotations

import csv
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import crud
from app.database.models import PromptTemplate


class TemplateService:
    """Service for loading, storing, and retrieving prompt templates."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def seed_from_file(self, session: AsyncSession) -> None:
        path = Path(self.settings.template_seed_path)
        if not path.exists():
            return
        await self.import_from_json(session, path)

    async def import_from_json(self, session: AsyncSession, file_path: str | Path) -> None:
        path = Path(file_path)
        payload = json.loads(path.read_text(encoding='utf-8'))
        for item in payload:
            await crud.upsert_prompt_template(
                session,
                key=item['key'],
                title=item['title'],
                category=item['category'],
                prompt_text=item['prompt_text'],
                is_active=bool(item.get('is_active', True)),
            )

    async def import_from_csv(self, session: AsyncSession, file_path: str | Path) -> None:
        path = Path(file_path)
        with path.open('r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                await crud.upsert_prompt_template(
                    session,
                    key=row['key'],
                    title=row['title'],
                    category=row['category'],
                    prompt_text=row['prompt_text'],
                    is_active=row.get('is_active', 'true').lower() == 'true',
                )

    async def list_active(self, session: AsyncSession) -> list[PromptTemplate]:
        return await crud.list_active_templates(session)

    async def list_categories(self, session: AsyncSession) -> list[str]:
        templates = await self.list_active(session)
        return sorted({template.category for template in templates})

    async def list_by_category(self, session: AsyncSession, category: str) -> list[PromptTemplate]:
        templates = await self.list_active(session)
        return [template for template in templates if template.category == category]

    async def get_by_key(self, session: AsyncSession, key: str) -> PromptTemplate | None:
        return await crud.get_template_by_key(session, key)
