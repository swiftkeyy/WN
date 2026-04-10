# AI Photo Telegram Bot

Production-oriented starter for a Telegram bot with remove.bg background removal, Gemini prompt intelligence, SQLite persistence, FastAPI webhook server, aiogram 3.x, SQLAlchemy 2.0, and Docker.

## Features

- Remove background from user photos via remove.bg
- Improve raw prompts via Gemini
- Trend template library with JSON seed import
- Free-form routing for caption helper / poster idea / avatar makeover / product photo / sticker pack prompt
- User history and task persistence
- Webhook or polling mode
- Ready for future image generation provider adapters

## Project structure

```text
app/
  main.py
  config.py
  bot.py
  api/
    webhook.py
    health.py
  handlers/
    start.py
    help.py
    photo.py
    text.py
    templates.py
    history.py
    states.py
  keyboards/
    main_menu.py
    templates_menu.py
  services/
    user_service.py
    history_service.py
    template_service.py
  ai/
    gemini_client.py
    prompt_router.py
    prompt_rewriter.py
  integrations/
    remove_bg_client.py
  database/
    base.py
    session.py
    models.py
    crud.py
  schemas/
    user.py
    task.py
    template.py
  prompt_templates/
    trend_templates.json
  utils/
    files.py
    logging.py
    constants.py
alembic/
  env.py
  versions/
    0001_initial.py
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

## Environment

Copy `.env.example` to `.env` and fill in:

- `TELEGRAM_BOT_TOKEN`
- `REMOVE_BG_API_KEY`
- `GEMINI_API_KEY`

Set `TELEGRAM_MODE=polling` for local dev or `TELEGRAM_MODE=webhook` plus public `TELEGRAM_WEBHOOK_URL` for staging/production.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

In polling mode, run the bot worker in a second terminal:

```bash
python -m app.run_polling
```

## Docker run

```bash
cp .env.example .env
docker compose up --build
```

## Webhook endpoint

- Health: `GET /api/health`
- Telegram webhook: `POST /api/webhook/telegram`

## Notes

- On startup the app seeds `prompt_templates` from `app/prompt_templates/trend_templates.json`.
- If Telegram channel templates cannot be parsed automatically, add or replace template items in JSON or import CSV later through `TemplateService.import_from_csv()`.
- This version uses SQLite for speed of launch and keeps services isolated enough to migrate later to Postgres/Redis.
