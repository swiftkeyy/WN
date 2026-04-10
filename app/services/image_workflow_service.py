from __future__ import annotations

from app.ai.gemini_client import GeminiClient
from app.integrations.remove_bg_client import RemoveBgClient
from app.providers.base import ImageJobRequest
from app.providers.factory import ImageProviderFactory
from app.utils.constants import BotModes


class ImageWorkflowService:
    def __init__(self) -> None:
        self.gemini = GeminiClient()
        self.remove_bg = RemoveBgClient()
        self.image_provider = ImageProviderFactory.create()

    async def process(
        self,
        *,
        mode: str,
        input_path: str,
        user_text: str | None = None,
        style_key: str | None = None,
    ) -> tuple[str, str]:
        if mode == BotModes.REMOVE_BG:
            return await self.remove_bg.remove_background(input_path), 'remove.bg'

        internal_prompt = await self.gemini.build_hidden_image_prompt(
            mode=mode,
            style_key=style_key,
            user_text=user_text or '',
        )
        job = ImageJobRequest(
            mode=mode,
            style_key=style_key,
            user_text=user_text,
            input_path=input_path,
            internal_prompt=internal_prompt,
        )
        output_path = await self.image_provider.process(job)
        return output_path, self.image_provider.provider_name
