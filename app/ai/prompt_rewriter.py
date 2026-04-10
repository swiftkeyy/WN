from app.ai.gemini_client import GeminiClient


class PromptRewriter:
    """High-level wrapper around Gemini prompt improvement."""

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self.gemini = gemini_client or GeminiClient()

    async def rewrite(self, text: str) -> dict[str, str]:
        return await self.gemini.improve_prompt(text)
