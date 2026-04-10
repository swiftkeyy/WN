from __future__ import annotations

from pathlib import Path

from app.providers.base import BaseImageProvider, ImageJobRequest


class ReplicateImageProvider(BaseImageProvider):
    provider_name = "replicate"

    async def run(self, job: ImageJobRequest) -> str:
        # Временный стабильный stub.
        # Позже сюда можно вернуть реальный вызов Replicate API.
        source = Path(job.input_path)
        output_dir = Path("./data/media/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{source.stem}_replicate.jpg"
        output_path.write_bytes(source.read_bytes())
        return str(output_path)

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
