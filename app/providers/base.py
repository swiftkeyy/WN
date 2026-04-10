from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ImageJobRequest:
    mode: str
    input_path: str
    prompt: str
    style_key: str | None = None


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

    async def run(self, job: ImageJobRequest) -> str:
        return await self.process_image(
            mode=job.mode,
            input_path=job.input_path,
            prompt=job.prompt,
            style_key=job.style_key,
        )
