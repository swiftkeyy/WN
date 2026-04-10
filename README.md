# AI Photo Telegram Bot

Версия с русским UX, inline-кнопками и реальными image providers.

## Что умеет

- удалять фон через remove.bg
- делать аватары, постеры, стикеры и товарные фото через подключаемый image provider
- использовать Gemini как внутренний оркестратор
- хранить историю задач

## Провайдеры изображений

Переключаются через `IMAGE_PROVIDER`:

- `openai` — OpenAI Images API edits
- `replicate` — Replicate + FLUX Kontext
- `fal` — fal + Nano Banana 2 Edit
- `none` — только remove.bg

## Быстрый старт

```bash
cp .env.example .env
alembic upgrade head
python -m app.run_polling
```

## Bothost

```bash
mkdir -p data/media/input data/media/output data/media/temp && alembic upgrade head && python -m app.run_polling
```

## Рекомендуемая конфигурация

### OpenAI

```env
IMAGE_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_IMAGE_MODEL=gpt-image-1.5
```

### Replicate

```env
IMAGE_PROVIDER=replicate
REPLICATE_API_KEY=...
REPLICATE_MODEL_OWNER=black-forest-labs
REPLICATE_MODEL_NAME=flux-kontext-max
```

### fal

```env
IMAGE_PROVIDER=fal
FAL_API_KEY=...
FAL_MODEL_ID=fal-ai/nano-banana-2/edit
```


## Multi-provider режим: Replicate + fal

Можно включить одновременную работу двух провайдеров с авто-переключением: сначала bot пробует Replicate, а если модель упала, таймаутнулась или вернула ошибку, автоматически идёт в fal.

```env
IMAGE_PROVIDER=multi
IMAGE_PROVIDER_CHAIN=replicate,fal
IMAGE_PROVIDER_PRIMARY_BY_MODE=avatar:replicate,poster:replicate,product:replicate,stickers:fal
REPLICATE_API_KEY=...
FAL_API_KEY=...
```

Логика по умолчанию:
- аватары, постеры, товарные фото -> Replicate, fallback на fal
- стикеры -> fal, fallback на Replicate

Если нужен другой порядок, просто поменяй `IMAGE_PROVIDER_CHAIN` и `IMAGE_PROVIDER_PRIMARY_BY_MODE`.
