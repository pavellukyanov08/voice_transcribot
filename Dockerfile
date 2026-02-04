FROM python:3.12-slim

WORKDIR /voice_transcribot

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc g++ curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.main"]