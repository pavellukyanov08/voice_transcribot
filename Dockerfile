FROM python:3.12-slim

WORKDIR /voice_transcribot

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic.ini .
COPY migrations/ ./migrations/
#COPY entrypoint.sh .

RUN chmod -R 755 /voice_transcribot

CMD ["python", "-m", "app.main"]