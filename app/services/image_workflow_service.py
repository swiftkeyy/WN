from __future__ import annotations

from dataclasses import dataclass

from app.ai.gemini_client import GeminiClient
from app.providers.factory import ImageProviderFactory


@dataclass
class ImageWorkflowResult:
    output_path: str
    provider: str


class ImageWorkflowService:
    def __init__(self) -> None:
        self.gemini_client = GeminiClient()
        self.provider_factory = ImageProviderFactory()

    async def process_image(
        self,
        mode: str,
        input_path: str,
        user_text: str = "",
        style_key: str | None = None,
    ) -> ImageWorkflowResult:
        hidden_prompt = await self.gemini_client.build_hidden_image_prompt(
            mode=mode,
            user_text=user_text,
            style_key=style_key,
        )

        provider = self.provider_factory.get_provider(mode=mode)

        output_path = await provider.process_image(
            mode=mode,
            input_path=input_path,
            prompt=hidden_prompt,
            style_key=style_key,
        )

        provider_name = getattr(provider, "provider_name", provider.__class__.__name__)

        return ImageWorkflowResult(
            output_path=output_path,
            provider=provider_name,
        )
