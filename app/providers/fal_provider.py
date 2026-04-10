from __future__ import annotations

import os
from pathlib import Path

import aiofiles
import aiohttp
import fal_client

from app.providers.base import BaseImageProvider, ImageJobRequest


class FalImageProvider(BaseImageProvider):
    provider_name = "fal"

    def __init__(self) -> None:
        self.model_ref = os.getenv(
            "FAL_MODEL_REF",
            "fal-ai/nano-banana/edit",
        )

    async def _download_output(self, url: str, output_path: Path) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                content = await resp.read()

        async with aiofiles.open(output_path, "wb") as f:
            await f.write(content)

        return str(output_path)

    async def run(self, job: ImageJobRequest) -> str:
        input_path = Path(job.input_path)
        output_dir = Path("./data/media/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}_fal.png"

        upload_url = await fal_client.upload_file_async(str(input_path))

        result = await fal_client.subscribe_async(
            self.model_ref,
            arguments={
                "prompt": job.prompt,
                "image_urls": [upload_url],
            },
        )

        images = result.get("images", [])
        if not images:
            raise RuntimeError("fal не вернул images")

        image_url = images[0].get("url")
        if not image_url:
            raise RuntimeError("fal не вернул URL результата")

        return await self._download_output(image_url, output_path)

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
