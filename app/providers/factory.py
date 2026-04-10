from __future__ import annotations

from app.config import get_settings
from app.providers.fal_provider import FalImageProvider
from app.providers.multi_provider import MultiImageProvider
from app.providers.replicate_provider import ReplicateImageProvider


class ImageProviderFactory:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_provider(self, mode: str):
        provider_name = (getattr(self.settings, "image_provider", "multi") or "multi").lower()

        if provider_name == "replicate":
            return ReplicateImageProvider()

        if provider_name == "fal":
            return FalImageProvider()

        return MultiImageProvider()
