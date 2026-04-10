from __future__ import annotations

import secrets
from pathlib import Path

import aiofiles
from aiogram.types import PhotoSize

from app.config import get_settings


settings = get_settings()


def ensure_media_dirs() -> None:
    """Create required media directories."""
    for directory in (settings.media_dir, settings.input_dir, settings.output_dir, settings.temp_dir):
        directory.mkdir(parents=True, exist_ok=True)


async def save_telegram_photo(bot, photo: PhotoSize, prefix: str = 'photo') -> str:
    """Download Telegram photo to the input directory and return its path."""
    ensure_media_dirs()
    file = await bot.get_file(photo.file_id)
    extension = Path(file.file_path or 'image.jpg').suffix or '.jpg'
    filename = f'{prefix}_{photo.file_unique_id}_{secrets.token_hex(4)}{extension}'
    destination = settings.input_dir / filename
    await bot.download(file, destination=destination)
    return str(destination)


async def save_bytes(content: bytes, output_path: Path) -> str:
    """Save raw bytes to a file asynchronously."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(output_path, 'wb') as f:
        await f.write(content)
    return str(output_path)


def build_output_path(stem: str, extension: str) -> Path:
    """Build a file path inside the output directory."""
    ensure_media_dirs()
    safe_extension = extension if extension.startswith('.') else f'.{extension}'
    return settings.output_dir / f'{stem}_{secrets.token_hex(4)}{safe_extension}'
