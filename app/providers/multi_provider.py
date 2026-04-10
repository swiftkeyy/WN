from __future__ import annotations

import logging

from app.config import get_settings
from app.providers.base import BaseImageProvider, ImageJobRequest
from app.providers.fal_provider import FalImageProvider
from app.providers.mock import UnconfiguredImageProvider
from app.providers.openai_provider import OpenAIImageProvider
from app.providers.replicate_provider import ReplicateImageProvider

logger = logging.getLogger(__name__)


class MultiImageProvider(BaseImageProvider):
    provider_name = 'multi'

    def __init__(self) -> None:
        self.settings = get_settings()
        self._providers = {
            'openai': OpenAIImageProvider,
            'replicate': ReplicateImageProvider,
            'fal': FalImageProvider,
            'none': UnconfiguredImageProvider,
        }

    def _parse_chain(self) -> list[str]:
        names = [item.strip().lower() for item in self.settings.image_provider_chain.split(',') if item.strip()]
        filtered = [name for name in names if name in self._providers and name != 'none']
        return filtered or ['replicate', 'fal']

    def _parse_primary_by_mode(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        raw = self.settings.image_provider_primary_by_mode.strip()
        if not raw:
            return mapping
        for chunk in raw.split(','):
            if ':' not in chunk:
                continue
            mode, provider = chunk.split(':', 1)
            mode = mode.strip().lower()
            provider = provider.strip().lower()
            if mode and provider in self._providers and provider != 'none':
                mapping[mode] = provider
        return mapping

    def _build_order(self, mode: str) -> list[str]:
        chain = self._parse_chain()
        primary = self._parse_primary_by_mode().get(mode.lower())
        if primary and primary in chain:
            return [primary] + [name for name in chain if name != primary]
        return chain

    async def process(self, job: ImageJobRequest) -> str:
        order = self._build_order(job.mode)
        errors: list[str] = []

        for provider_key in order:
            provider = self._providers[provider_key]()
            try:
                result = await provider.process(job)
                self.provider_name = provider.provider_name
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning('Провайдер %s не справился: %s', provider_key, exc)
                errors.append(f'{provider_key}: {exc}')

        raise RuntimeError('Не удалось обработать изображение ни одним провайдером. ' + ' | '.join(errors))
