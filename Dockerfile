FROM python:3.12-slim

WORKDIR /voice_transcribot

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc g++ curl \
    apt install ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
COPY db_start.sh .

RUN chmod +x ./db_start.sh

ENTRYPOINT ["./db_start.sh"]
CMD ["python", "-m", "app.main"]