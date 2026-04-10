from app.ai.gemini_client import GeminiClient


class PromptRouter:
    """Routes free-form text requests to the proper bot mode."""

    def __init__(self, gemini_client: GeminiClient | None = None) -> None:
        self.gemini = gemini_client or GeminiClient()

    async def route(self, text: str) -> str:
        return await self.gemini.classify_request(text)
