FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ai_services/requirements.txt /app/ai_services/requirements.txt
RUN pip install --no-cache-dir -r /app/ai_services/requirements.txt

COPY backend/src /app/backend/src
COPY ai_services /app/ai_services
COPY .env* /app/

ENV PYTHONPATH=/app/backend:/app/ai_services
RUN mkdir -p /app/data/faiss_index

CMD ["python", "-m", "ai_services.workers.vector_ingestion_worker"]
