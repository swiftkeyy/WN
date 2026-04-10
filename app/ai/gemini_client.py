from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Async Gemini REST client with safe fallbacks."""

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

    async def improve_prompt(self, text: str) -> dict[str, str]:
        """Improve a raw prompt and return multiple production-ready variants."""
        prompt = f"""
You are a prompt optimization assistant for AI image workflows.
Return strict JSON with keys: short_version, detailed_version, trend_version, detected_goal.
User prompt: {text}
Constraints:
- short_version: one strong concise image prompt.
- detailed_version: expanded production-ready prompt.
- trend_version: social-media-friendly trendy visual variant.
- detected_goal: one short label.
Output only JSON.
""".strip()
        try:
            raw = await self._generate_text(prompt, response_mime_type='application/json')
            parsed = json.loads(raw)
            return {
                'short_version': parsed.get('short_version', text.strip()),
                'detailed_version': parsed.get('detailed_version', text.strip()),
                'trend_version': parsed.get('trend_version', text.strip()),
                'detected_goal': parsed.get('detected_goal', 'general'),
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini improve_prompt failed: %s', exc)
            base = text.strip()
            return {
                'short_version': base,
                'detailed_version': f'{base}. High detail, clean composition, cinematic lighting, premium quality.',
                'trend_version': f'{base}. Viral social media aesthetic, punchy composition, polished editing, premium visual impact.',
                'detected_goal': 'general',
            }

    async def classify_request(self, text: str) -> str:
        """Classify user intent into a supported bot action."""
        prompt = f"""
Classify the user request into exactly one label from this list:
remove_bg, prompt_improve, template_apply, ai_caption, poster_idea, avatar_makeover, product_photo, sticker_pack, general_help.
User request: {text}
Output only the label.
""".strip()
        try:
            label = (await self._generate_text(prompt)).strip().lower()
            allowed = {
                'remove_bg',
                'prompt_improve',
                'template_apply',
                'ai_caption',
                'poster_idea',
                'avatar_makeover',
                'product_photo',
                'sticker_pack',
                'general_help',
            }
            if label in allowed:
                return label
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini classify_request failed: %s', exc)

        lowered = text.lower()
        if 'фон' in lowered or 'background' in lowered:
            return 'remove_bg'
        if 'стикер' in lowered or 'sticker' in lowered:
            return 'sticker_pack'
        if 'аватар' in lowered or 'avatar' in lowered:
            return 'avatar_makeover'
        if 'product' in lowered or 'товар' in lowered:
            return 'product_photo'
        if 'poster' in lowered or 'постер' in lowered:
            return 'poster_idea'
        if 'caption' in lowered or 'подпись' in lowered or 'идея' in lowered:
            return 'ai_caption'
        return 'prompt_improve'

    async def build_template_prompt(
        self,
        template_key: str,
        user_input: str,
        base_template: str | None = None,
    ) -> str:
        """Build a final prompt for a selected template."""
        prompt = f"""
You are building a final AI image prompt.
Template key: {template_key}
Base template: {base_template or 'Use best practices'}
User input: {user_input}
Return only the final prompt text.
Rules:
- Keep it actionable for image generation tools.
- Preserve the template intent.
- Add style, lighting, composition, and detail cues when useful.
- Do not explain.
""".strip()
        try:
            return await self._generate_text(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini build_template_prompt failed: %s', exc)
            seed = base_template or 'Create a high-quality visual based on the user request.'
            return f'{seed} User-specific details: {user_input}. Output should look polished, premium, and ready for modern AI image workflows.'

    async def generate_helper_reply(self, mode: str, text: str) -> str:
        """Generate a short user-facing helper message for non-image tasks."""
        prompt = f"""
You are an AI assistant inside a Telegram bot for image creators.
Mode: {mode}
User input: {text}
Return a concise but useful answer in Russian.
If relevant, include one final ready-to-copy prompt block in plain text.
Do not use markdown headings.
""".strip()
        try:
            return await self._generate_text(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Gemini generate_helper_reply failed: %s', exc)
            fallback = {
                'ai_caption': f'Идея для визуала: {text}\n\nГотовый промпт: Create a clean social media visual based on: {text}. Modern composition, strong focal point, polished details.',
                'poster_idea': f'Готовый постер-промпт: Cinematic poster concept based on {text}. Dramatic lighting, bold typography area, premium composition.',
                'avatar_makeover': f'Готовый аватар-промпт: Stylish portrait makeover based on {text}. Sharp face detail, premium lighting, modern editorial finish.',
                'product_photo': f'Готовый product-промпт: Premium product shot based on {text}. Soft studio light, sharp materials, luxury ad composition.',
                'sticker_pack': f'Готовый sticker-промпт: Sticker pack concept based on {text}. Consistent character style, clean outlines, transparent background.',
                'general_help': 'Я умею удалить фон, улучшить промпт, применить шаблон и собрать идею для визуала. Нажми кнопку в меню или просто напиши задачу.',
            }
            return fallback.get(mode, fallback['general_help'])
