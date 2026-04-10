FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     curl     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/media/input /app/data/media/output /app/data/media/temp

CMD ["bash", "-lc", "mkdir -p data/media/input data/media/output data/media/temp && alembic upgrade head && python -m app.run_polling"]
