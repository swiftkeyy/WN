from app.providers.base import BaseImageProvider
from app.providers.mock import UnconfiguredImageProvider


class ImageProviderFactory:
    @staticmethod
    def create() -> BaseImageProvider:
        return UnconfiguredImageProvider()
