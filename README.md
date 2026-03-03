Wichtig für deine Django Engine

Du brauchst:

Modell installiert

Server aktiv

Du brauchst nicht zwingend ollama run.

Für Backend Nutzung reicht:

ollama serve

und dein Django macht HTTP Calls.

## Prüfe ob Ollama läuft
Ollama besteht aus zwei Schichten:
1. Server Prozess 
2. Installierte Modellgewichte

```bash
ollama list
```
listet alle Model auf

ollama pull deepseek-coder:6.7b

## Gui aufrufen 
http://127.0.0.1:8000/api/code/


## Erstelle Dockerfile
```bash
cat <<'EOF' > Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
EOF
```

## Erstelle eine docker compose 

```bash
cat <<'EOF' > docker-compose.yml
version: "3.9"

services:

  postgres:
    image: postgres:16
    container_name: ai_postgres
    restart: always
    environment:
      POSTGRES_DB: ai_db
      POSTGRES_USER: ai_user
      POSTGRES_PASSWORD: strongpassword
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  ai_code:
    build: .
    container_name: ai_code
    restart: always
    ports:
      - "8003:8000"
    env_file:
      - .env
    depends_on:
      - postgres
      - ollama
    environment:
      DB_NAME: ai_db
      DB_USER: ai_user
      DB_PASSWORD: strongpassword
      DB_HOST: postgres
      DB_PORT: 5432
    volumes:
      - .:/app

  ollama:
    image: ollama/ollama
    container_name: ai_ollama
    restart: always
    volumes:
      - ollama_data:/root/.ollama

volumes:
  pg_data:
  ollama_data:
EOF
```
