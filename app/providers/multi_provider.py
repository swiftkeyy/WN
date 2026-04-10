from __future__ import annotations

from app.providers.base import BaseImageProvider, ImageJobRequest
from app.providers.fal_provider import FalImageProvider
from app.providers.replicate_provider import ReplicateImageProvider


class MultiImageProvider(BaseImageProvider):
    provider_name = "multi"

    def __init__(self) -> None:
        self.replicate_provider = ReplicateImageProvider()
        self.fal_provider = FalImageProvider()

    def _pick_chain(self, mode: str):
        if mode == "stickers":
            return [self.fal_provider, self.replicate_provider]
        return [self.replicate_provider, self.fal_provider]

    async def run(self, job: ImageJobRequest) -> str:
        last_error: Exception | None = None

        for provider in self._pick_chain(job.mode):
            try:
                return await provider.run(job)
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        if last_error is not None:
            raise last_error

        raise RuntimeError("Не удалось обработать изображение")

    async def process_image(
        self,
        mode: str,
        input_path: str,
        prompt: str,
        style_key: str | None = None,
    ) -> str:
        job = ImageJobRequest(
            mode=mode,
            input_path=input_path,
            prompt=prompt,
            style_key=style_key,
        )
        return await self.run(job)
