# AI Photo Telegram Bot

Версия с русским UX и inline-кнопками.

## Что делает сейчас

- реально удаляет фон через remove.bg
- ведёт историю задач
- использует Gemini как внутренний мозг для image workflow
- меню полностью на русском языке
- интерфейс построен на inline-кнопках

## Важно

Режимы `Аватар`, `Постер`, `Стикеры`, `Товарное фото` уже переведены на архитектуру `ready-made image output bot`, но для них нужен отдельный image provider. В проекте оставлен адаптер и фабрика провайдеров. После подключения реального image editing API эти режимы начнут отдавать готовые изображения без переделки хендлеров.

## Запуск

```bash
alembic upgrade head
python -m app.run_polling
```

## Bothost

Рекомендуемый стартовый запуск:

```bash
mkdir -p data/media/input data/media/output data/media/temp && alembic upgrade head && python -m app.run_polling
```
