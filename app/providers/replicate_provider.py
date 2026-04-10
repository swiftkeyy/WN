from __future__ import annotations

import os
from pathlib import Path

import aiofiles
import aiohttp
import replicate

from app.providers.base import BaseImageProvider, ImageJobRequest


class ReplicateImageProvider(BaseImageProvider):
    provider_name = "replicate"

    def __init__(self) -> None:
        self.model_ref = os.getenv(
            "REPLICATE_MODEL_REF",
            "black-forest-labs/flux-kontext-max",
        )

    async def _download_output(self, output, output_path: Path) -> str:
        url = None

        if isinstance(output, list) and output:
            first = output[0]
            if hasattr(first, "url"):
                url = first.url
            elif isinstance(first, str):
                url = first
        elif hasattr(output, "url"):
            url = output.url
        elif isinstance(output, str):
            url = output

        if not url:
            raise RuntimeError("Replicate не вернул URL результата")

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
        output_path = output_dir / f"{input_path.stem}_replicate.png"

        with input_path.open("rb") as image_file:
            output = await replicate.async_run(
                self.model_ref,
                input={
                    "input_image": image_file,
                    "prompt": job.prompt,
                },
            )

        return await self._download_output(output, output_path)

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
