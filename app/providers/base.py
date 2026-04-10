from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ImageJobRequest:
    mode: str
    style_key: str | None
    user_text: str | None
    input_path: str
    internal_prompt: str


class BaseImageProvider:
    provider_name: str = 'base'

    async def process(self, job: ImageJobRequest) -> str:
        raise NotImplementedError
