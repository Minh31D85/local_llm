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

COPY pyproject.toml .

RUN pip install --upgrade pip \
    && pip install .

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
    env_file:
      - .env
    volumes:
      - pg_data:/var/lib/postgresql/data

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

## Erstelle envirnment
```bash
cat <<'EOF' > .env
DEBUG=False
SECRET_KEY=change_this_secret_key

POSTGRES_DB=ai_db
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-coder:6.7b
EOF
```

## Alles sauber starten
```bash
sudo docker compose down -v
sudo docker compose up --build -d
```

## Migration ausführen


## Teste Ollama Container 
Interner Test
```bash
docker exec -it ai_ollama ollama pull deepseek-coder:6.7b
```

Terminal Test
```bash
curl -X POST http://192.168.178.98:8003/api/code/generate/ \
-H "Content-Type: application/json" \
-d '{"prompt":"write a python function that adds two numbers","mode":"generate"}'
```