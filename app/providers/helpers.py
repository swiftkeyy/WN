from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import httpx

from app.utils.files import build_output_path, save_bytes


def guess_content_type(path: str | Path) -> str:
    content_type, _ = mimetypes.guess_type(str(path))
    return content_type or 'application/octet-stream'


def file_to_data_uri(path: str | Path) -> str:
    file_path = Path(path)
    mime = guess_content_type(file_path)
    payload = base64.b64encode(file_path.read_bytes()).decode('utf-8')
    return f'data:{mime};base64,{payload}'


async def download_to_output(url: str, stem: str, extension: str | None = None, timeout_seconds: int = 180) -> str:
    suffix = extension or Path(url.split('?', 1)[0]).suffix or '.png'
    output_path = build_output_path(stem, suffix)
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
    return await save_bytes(response.content, output_path)
