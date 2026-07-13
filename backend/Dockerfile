FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -d /app -s /sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn>=21.0.0

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R appuser:appuser /app \
    && mkdir -p /app/uploads/logos \
    && chown -R appuser:appuser /app/uploads

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

# ponytail: gunicorn+uvicorn workers for prod; override CMD in compose.override for dev (single uvicorn)
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
