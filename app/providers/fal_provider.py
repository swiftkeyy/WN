from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.config import get_settings
from app.providers.base import BaseImageProvider, ImageJobRequest
from app.providers.helpers import download_to_output, file_to_data_uri
from app.utils.constants import BotModes

logger = logging.getLogger(__name__)


class FalImageProvider(BaseImageProvider):
    provider_name = 'fal'

    def __init__(self) -> None:
        self.settings = get_settings()
        self.queue_base = 'https://queue.fal.run'

    async def process(self, job: ImageJobRequest) -> str:
        if not self.settings.fal_api_key:
            raise RuntimeError('FAL_API_KEY не настроен')

        endpoint = self.settings.fal_model_id.strip('/')
        submit_url = f'{self.queue_base}/{endpoint}'
        headers = {
            'Authorization': f'Key {self.settings.fal_api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'prompt': job.internal_prompt,
            'image_urls': [file_to_data_uri(job.input_path)],
            'num_images': 1,
            'output_format': 'png',
            'aspect_ratio': 'auto',
            'resolution': '1K',
            'limit_generations': True,
        }

        timeout = httpx.Timeout(self.settings.fal_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.post(submit_url, headers=headers, json=payload)
            if response.status_code >= 400:
                logger.error('fal submit failed: %s %s', response.status_code, response.text)
                raise RuntimeError(f'fal submit failed: {response.text}')

            request_info = response.json()
            result = await self._wait_result(client, request_info)
            output_url = self._extract_output_url(result)
            return await download_to_output(output_url, f'{job.mode}_fal', timeout_seconds=self.settings.fal_timeout_seconds)

    async def _wait_result(self, client: httpx.AsyncClient, request_info: dict[str, Any]) -> dict[str, Any]:
        status_url = request_info.get('status_url')
        response_url = request_info.get('response_url')
        if not status_url or not response_url:
            raise RuntimeError('fal не вернул status_url/response_url')

        headers = {'Authorization': f'Key {self.settings.fal_api_key}'}
        interval = max(1, int(self.settings.fal_poll_interval_seconds))

        for _ in range(180):
            status_resp = await client.get(f'{status_url}?logs=1', headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            status = status_data.get('status')

            if status == 'COMPLETED':
                if status_data.get('error'):
                    raise RuntimeError(f"fal job failed: {status_data.get('error')}")
                result_resp = await client.get(response_url, headers=headers)
                result_resp.raise_for_status()
                return result_resp.json()

            if status_data.get('error'):
                raise RuntimeError(f"fal job failed: {status_data.get('error')}")

            await asyncio.sleep(interval)

        raise RuntimeError('fal превысил время ожидания результата')

    @staticmethod
    def _extract_output_url(result: dict[str, Any]) -> str:
        images = result.get('images') or []
        if images and isinstance(images[0], dict) and images[0].get('url'):
            return images[0]['url']
        raise RuntimeError('fal не вернул URL результата')
