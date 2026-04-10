from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings
from app.utils.constants import MODE_TITLES

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini-клиент для внутренней логики бота."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.gemini_api_url.rstrip('/')
        self.model = self.settings.gemini_model

    async def _generate_text(self, prompt: str, response_mime_type: str = 'text/plain') -> str:
        if not self.settings.gemini_api_key:
            raise RuntimeError('GEMINI_API_KEY is not configured')

        url = f'{self.base_url}/{self.model}:generateContent'
        params = {'key': self.settings.gemini_api_key}
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0.7,
                'responseMimeType': response_mime_type,
            },
        }

        timeout = httpx.Timeout(self.settings.gemini_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get('candidates', [])
        if not candidates:
            raise RuntimeError('Gemini returned no candidates')

        parts = candidates[0].get('content', {}).get('parts', [])
        text = ''.join(part.get('text', '') for part in parts if 'text' in part).strip()
        if not text:
            raise RuntimeError('Gemini response contained no text')
        return text

    async def build_hidden_image_prompt(self, mode: str, style_key: str | None, user_text: str) -> str:
        prompt = f"""
Ты — внутренний AI-оркестратор Telegram-бота по обработке фото.
Твоя задача: создать скрытый production-ready prompt для image-to-image workflow.
Пользователь этот prompt не увидит.

Режим: {mode}
Название режима: {MODE_TITLES.get(mode, mode)}
Стиль: {style_key or 'не указан'}
Пожелания пользователя: {user_text or 'без доп. пожеланий'}

Верни только один готовый prompt на английском языке.
Он должен быть пригоден для image editing / restyle workflow.
Без пояснений.
""".strip()
        try:
            return await self._generate_text(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini build_hidden_image_prompt failed: %s', exc)
            return (
                f'{MODE_TITLES.get(mode, mode)} based on uploaded photo. '
                f'Style: {style_key or "default"}. '
                f'User wishes: {user_text or "none"}. '
                'High detail, premium quality, realistic lighting, clean composition.'
            )

    async def generate_help_text(self) -> str:
        prompt = """
Составь короткую справку на русском языке для Telegram-бота, который сам обрабатывает фотографии.
Режимы: удалить фон, аватар, постер, стикеры, товарное фото.
Тон: короткий, понятный, дружелюбный.
Не используй markdown-заголовки.
""".strip()
        try:
            return await self._generate_text(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini generate_help_text failed: %s', exc)
            return (
                'Я сам обрабатываю фото и возвращаю готовый результат.\n\n'
                'Доступные режимы:\n'
                '• Удалить фон\n'
                '• Сделать аватар\n'
                '• Сделать постер\n'
                '• Сделать стикеры\n'
                '• Оформить товарное фото\n\n'
                'Выбери режим кнопками, затем пришли фото. При желании можно добавить подпись с пожеланиями.'
            )

    async def summarize_history_title(self, mode: str, style_key: str | None) -> str:
        title = MODE_TITLES.get(mode, mode)
        if style_key:
            return f'{title} / {style_key}'
        return title
