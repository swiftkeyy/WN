from __future__ import annotations

import json
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Клиент Gemini API с безопасным fallback."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.gemini_api_url.rstrip("/")
        self.model = self.settings.gemini_model

    async def _generate_text(
        self,
        prompt: str,
        response_mime_type: str = "text/plain",
    ) -> str:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY не настроен")

        url = f"{self.base_url}/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "responseMimeType": response_mime_type,
            },
        }

        timeout = httpx.Timeout(self.settings.gemini_timeout_seconds)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    headers={
                        "x-goog-api-key": self.settings.gemini_api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            body = ""
            try:
                body = exc.response.text[:500] if exc.response else ""
            except Exception:
                body = ""
            logger.error(
                "Gemini API HTTP error: status=%s, model=%s, response=%s",
                status,
                self.model,
                body,
            )
            raise
        except Exception as exc:
            logger.exception("Gemini API request failed: model=%s error=%s", self.model, exc)
            raise

        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini не вернул candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if "text" in part).strip()

        if not text:
            raise RuntimeError("Gemini вернул пустой текст")

        return text

    async def improve_prompt(self, text: str) -> dict[str, str]:
        prompt = f"""
Ты AI-ассистент для генерации и обработки изображений.
Верни JSON со строго такими ключами:
short_version, detailed_version, trend_version, detected_goal

Запрос пользователя:
{text}

Требования:
- short_version: короткая сильная версия
- detailed_version: расширенная продакшн-версия
- trend_version: версия под трендовый визуал
- detected_goal: короткая метка цели
Верни только JSON.
""".strip()

        try:
            raw = await self._generate_text(prompt, response_mime_type="application/json")
            parsed = json.loads(raw)
            return {
                "short_version": parsed.get("short_version", text.strip()),
                "detailed_version": parsed.get("detailed_version", text.strip()),
                "trend_version": parsed.get("trend_version", text.strip()),
                "detected_goal": parsed.get("detected_goal", "general"),
            }
        except Exception as exc:
            logger.warning("Gemini improve_prompt fallback: %s", exc)
            base = text.strip()
            return {
                "short_version": base,
                "detailed_version": f"{base}. Высокая детализация, чистая композиция, аккуратный свет, качественная обработка.",
                "trend_version": f"{base}. Современный трендовый стиль, выразительный кадр, премиальная визуальная подача.",
                "detected_goal": "general",
            }

    async def classify_request(self, text: str) -> str:
        prompt = f"""
Классифицируй запрос пользователя строго в один из вариантов:
remove_bg, avatar, poster, stickers, product, help

Запрос:
{text}

Верни только одно слово из списка.
""".strip()

        try:
            result = (await self._generate_text(prompt)).strip().lower()
            allowed = {"remove_bg", "avatar", "poster", "stickers", "product", "help"}
            if result in allowed:
                return result
        except Exception as exc:
            logger.warning("Gemini classify_request fallback: %s", exc)

        lowered = text.lower()
        if "фон" in lowered or "background" in lowered:
            return "remove_bg"
        if "аватар" in lowered:
            return "avatar"
        if "постер" in lowered:
            return "poster"
        if "стикер" in lowered:
            return "stickers"
        if "товар" in lowered or "product" in lowered:
            return "product"
        return "help"

    async def build_hidden_image_prompt(
        self,
        mode: str,
        user_text: str = "",
        style_key: str | None = None,
    ) -> str:
        """
        Строит скрытый prompt для image provider.
        style_key оставлен для совместимости со старым кодом.
        """

        style_hint = f"\nСтиль: {style_key}" if style_key else ""

        prompt = f"""
Ты — внутренний AI-оркестратор Telegram-бота по обработке фото.
Нужно составить один качественный скрытый prompt для image-to-image обработки.

Режим: {mode}{style_hint}
Пожелание пользователя: {user_text or "без дополнительных пожеланий"}

Верни только готовый prompt без пояснений.

Требования по режимам:
- avatar: сильный портрет, красивый свет, аккуратная ретушь, акцент на лице
- poster: кинематографичность, драматичный свет, выразительная композиция
- stickers: стикерный стиль, чистые контуры, читаемые эмоции, серия стикеров
- product: коммерческий вид, чистая подача, студийный свет, premium look
""".strip()

        try:
            return await self._generate_text(prompt)
        except Exception as exc:
            logger.warning(
                "Gemini build_hidden_image_prompt fallback: mode=%s style=%s error=%s",
                mode,
                style_key,
                exc,
            )

            style_part = f" Стиль: {style_key}." if style_key else ""

            fallback_map = {
                "avatar": (
                    f"Сделай стильный портрет по загруженному фото.{style_part} "
                    f"Пожелание пользователя: {user_text or 'без дополнительных пожеланий'}. "
                    f"Естественная ретушь, акцент на лице, качественный свет, современный премиальный стиль."
                ),
                "poster": (
                    f"Сделай кинематографичный постер по загруженному фото.{style_part} "
                    f"Пожелание пользователя: {user_text or 'без дополнительных пожеланий'}. "
                    f"Драматичный свет, сильная композиция, выразительная атмосфера, эффектный визуальный стиль."
                ),
                "stickers": (
                    f"Сделай набор стикеров по загруженному фото.{style_part} "
                    f"Пожелание пользователя: {user_text or 'без дополнительных пожеланий'}. "
                    f"Чистые контуры, яркие эмоции, стикерный стиль, аккуратная изоляция персонажа."
                ),
                "product": (
                    f"Сделай коммерческое товарное фото по загруженному изображению.{style_part} "
                    f"Пожелание пользователя: {user_text or 'без дополнительных пожеланий'}. "
                    f"Чистый фон, студийный свет, аккуратные материалы, рекламный premium look."
                ),
            }
            return fallback_map.get(
                mode,
                f"Обработай изображение по фото.{style_part} "
                f"Пожелание пользователя: {user_text or 'без дополнительных пожеланий'}. "
                f"Качественный результат, чистая композиция, аккуратная визуальная подача.",
            )

    async def generate_helper_reply(self, mode: str, text: str) -> str:
        prompt = f"""
Ты помощник внутри Telegram-бота по обработке фото.
Режим: {mode}
Текст пользователя: {text}

Ответь кратко и по-русски.
Не показывай внутренние промпты.
Объясни следующий шаг пользователя.
""".strip()

        try:
            return await self._generate_text(prompt)
        except Exception as exc:
            logger.warning("Gemini generate_helper_reply fallback: %s", exc)
            fallback = {
                "avatar": "Пришли фото и коротко напиши, какой стиль нужен для аватара.",
                "poster": "Пришли фото и напиши идею постера одним сообщением.",
                "stickers": "Пришли фото и опиши настроение для стикеров: мемно, мило, аниме или что-то своё.",
                "product": "Пришли фото товара и коротко опиши, какой нужен рекламный стиль.",
                "remove_bg": "Пришли фото, и я уберу фон.",
                "help": "Я умею убрать фон, сделать аватар, постер, стикеры и оформить товарное фото. Выбери режим и пришли фото.",
            }
            return fallback.get(mode, fallback["help"])
