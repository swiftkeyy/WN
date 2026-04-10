from __future__ import annotations

from abc import ABC, abstractmethod


class BaseImageProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def process_image(
        self,
        mode: str,
        input_path: str,
        prompt: str,
        style_key: str | None = None,
    ) -> str:
        raise NotImplementedError
