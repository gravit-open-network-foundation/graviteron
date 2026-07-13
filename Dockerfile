FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

EXPOSE 8000

ENV REDIS_URL=""
ENV ADVERSARIAL_THRESHOLD="0.7"
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "uvicorn", "graviteron.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
