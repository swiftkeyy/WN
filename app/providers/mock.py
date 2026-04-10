from app.providers.base import BaseImageProvider, ImageJobRequest


class UnconfiguredImageProvider(BaseImageProvider):
    async def process(self, job: ImageJobRequest) -> str:
        raise RuntimeError(
            'Для этого режима ещё не подключён движок обработки изображений. '
            'Режим удаления фона уже работает. Остальные режимы активируются после подключения image provider.'
        )
