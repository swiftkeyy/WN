from __future__ import annotations

import base64
import logging
from pathlib import Path

import httpx

from app.config import get_settings
from app.providers.base import BaseImageProvider, ImageJobRequest
from app.providers.helpers import guess_content_type
from app.utils.constants import BotModes
from app.utils.files import build_output_path, save_bytes

logger = logging.getLogger(__name__)


class OpenAIImageProvider(BaseImageProvider):
    provider_name = 'openai'

    def __init__(self) -> None:
        self.settings = get_settings()

    async def process(self, job: ImageJobRequest) -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError('OPENAI_API_KEY не настроен')

        payload = {
            'model': self.settings.openai_image_model,
            'prompt': job.internal_prompt,
            'quality': self.settings.openai_image_quality,
            'response_format': 'b64_json',
            'output_format': 'png',
            'n': '1',
        }

        if job.mode == BotModes.STICKERS:
            payload['background'] = 'transparent'

        size = self.settings.openai_image_size.strip()
        if size:
            payload['size'] = size

        headers = {'Authorization': f'Bearer {self.settings.openai_api_key}'}
        timeout = httpx.Timeout(self.settings.openai_timeout_seconds)
        image_path = Path(job.input_path)

        async with httpx.AsyncClient(timeout=timeout) as client:
            with image_path.open('rb') as file_handle:
                files = {'image': (image_path.name, file_handle, guess_content_type(image_path))}
                response = await client.post(
                    'https://api.openai.com/v1/images/edits',
                    headers=headers,
                    data=payload,
                    files=files,
                )

        if response.status_code >= 400:
            logger.error('OpenAI images edit failed: %s %s', response.status_code, response.text)
            raise RuntimeError(f'OpenAI image edit failed: {response.text}')

        data = response.json()
        items = data.get('data') or []
        if not items:
            raise RuntimeError('OpenAI не вернул изображение')

        item = items[0]
        if item.get('b64_json'):
            image_bytes = base64.b64decode(item['b64_json'])
            output_path = build_output_path(f'{job.mode}_openai', '.png')
            return await save_bytes(image_bytes, output_path)

        if item.get('url'):
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                file_response = await client.get(item['url'])
                file_response.raise_for_status()
            output_path = build_output_path(f'{job.mode}_openai', '.png')
            return await save_bytes(file_response.content, output_path)

        raise RuntimeError('OpenAI вернул неожиданный формат ответа')
