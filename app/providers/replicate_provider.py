from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import aiofiles
import replicate

from app.config import get_settings
from app.providers.base import BaseImageProvider, ImageJobRequest
from app.utils.files import build_output_path

logger = logging.getLogger(__name__)


class ReplicateImageProvider(BaseImageProvider):
    provider_name = 'replicate'

    def __init__(self) -> None:
        self.settings = get_settings()

    async def process(self, job: ImageJobRequest) -> str:
        if not self.settings.replicate_api_key:
            raise RuntimeError('REPLICATE_API_KEY не настроен')

        model_ref = f'{self.settings.replicate_model_owner}/{self.settings.replicate_model_name}'
        input_payload = {
            'prompt': job.internal_prompt,
            'input_image': open(job.input_path, 'rb'),
            'aspect_ratio': 'match_input_image',
        }

        try:
            output = await asyncio.to_thread(
                replicate.run,
                model_ref,
                input=input_payload,
                wait=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('Replicate run failed: %s', exc)
            raise RuntimeError(f'Replicate run failed: {exc}') from exc
        finally:
            file_obj = input_payload['input_image']
            file_obj.close()

        return await self._save_output(output, job.mode)

    async def _save_output(self, output: Any, mode: str) -> str:
        file_output = output[0] if isinstance(output, list) else output

        if hasattr(file_output, 'read'):
            image_bytes = await asyncio.to_thread(file_output.read)
            source_name = getattr(file_output, 'url', None) or ''
            suffix = Path(str(source_name).split('?', 1)[0]).suffix or '.png'
            output_path = build_output_path(f'{mode}_replicate', suffix)
            async with aiofiles.open(output_path, 'wb') as f:
                await f.write(image_bytes)
            return str(output_path)

        if isinstance(file_output, str):
            raise RuntimeError('Replicate вернул URL вместо FileOutput. Используй актуальную версию пакета replicate.')

        raise RuntimeError('Replicate вернул неожиданный формат результата')
