from app.config import get_settings
from app.providers.base import BaseImageProvider
from app.providers.fal_provider import FalImageProvider
from app.providers.mock import UnconfiguredImageProvider
from app.providers.multi_provider import MultiImageProvider
from app.providers.openai_provider import OpenAIImageProvider
from app.providers.replicate_provider import ReplicateImageProvider


class ImageProviderFactory:
    @staticmethod
    def create() -> BaseImageProvider:
        settings = get_settings()
        provider = settings.image_provider.strip().lower()

        if provider == 'openai':
            return OpenAIImageProvider()
        if provider == 'replicate':
            return ReplicateImageProvider()
        if provider == 'fal':
            return FalImageProvider()
        if provider == 'multi':
            return MultiImageProvider()
        return UnconfiguredImageProvider()
