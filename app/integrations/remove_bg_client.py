from __future__ import annotations

import logging
from pathlib import Path

import httpx

from app.config import get_settings
from app.utils.files import build_output_path, save_bytes

logger = logging.getLogger(__name__)


class RemoveBgClient:
    """Async client for the remove.bg API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def remove_background(self, input_path: str) -> str:
        """Send an image to remove.bg and save the transparent PNG result."""
        if not self.settings.remove_bg_api_key:
            raise RuntimeError('REMOVE_BG_API_KEY is not configured')

        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f'Input file not found: {input_path}')

        output_path = build_output_path(path.stem + '_no_bg', '.png')
        headers = {'X-Api-Key': self.settings.remove_bg_api_key}
        data = {'size': 'auto', 'format': 'png'}
        timeout = httpx.Timeout(self.settings.remove_bg_timeout_seconds)

        async with httpx.AsyncClient(timeout=timeout) as client:
            with path.open('rb') as file_handle:
                files = {'image_file': (path.name, file_handle, 'application/octet-stream')}
                response = await client.post(
                    self.settings.remove_bg_api_url,
                    headers=headers,
                    data=data,
                    files=files,
                )

        if response.status_code >= 400:
            logger.error('remove.bg error %s: %s', response.status_code, response.text)
            raise RuntimeError(f'remove.bg failed with status {response.status_code}: {response.text}')

        return await save_bytes(response.content, output_path)
