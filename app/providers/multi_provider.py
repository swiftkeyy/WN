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
                if hasattr(provider, "run"):
                    return await provider.run(job)

                return await provider.process_image(
                    mode=job.mode,
                    input_path=job.input_path,
                    prompt=job.prompt,
                    style_key=job.style_key,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue

        if last_error is not None:
            raise last_error

        raise RuntimeError("Не удалось выбрать provider для обработки изображения")

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
