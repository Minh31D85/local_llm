### AI Code

Self-hosted AI Code Generation Service basierend auf:

- **Django / Django REST** – Backend und API
- **PostgreSQL** – Persistente Datenbank
- **Ollama** – Lokale Large Language Models (LLMs)
- **uv** – schneller Python Dependency Manager
- **Docker / Docker Compose** – Containerisierte Infrastruktur

Die Anwendung ermöglicht lokale Codegenerierung über eine API sowie eine einfache Web-GUI.


## Features

Lokale LLM Codegenerierung

Unterstützung mehrerer Modelle

deepseek-coder

mixtral

llama3

qwen coder

REST API für Codegenerierung

Docker-basierte Installation

PostgreSQL Datenbank

Streamingfähige Antworten

Web GUI


## Voraussetzungen

Folgende Software wird benötigt:

Docker

Docker Compose

Linux / TrueNAS / Debian / Ubuntu Server


## Environment Variablen
SERVER_IP	= IP Adresse oder Hostname des Servers
HOST_PORT	= Port unter dem der Server erreichbar ist
SECRET_KEY = Sicherheitsschlüssel für Django. Muss frei gewählt werden und geheim bleiben. Darf nicht veröffentlicht werden


## Erstelle Dockerfile
```bash
cat <<'EOF' > Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# uv Stabilitätsfix für ZFS / TrueNAS
ENV UV_LINK_MODE=copy
ENV UV_CONCURRENT_INSTALLS=1

WORKDIR /app

# uv installieren
RUN pip install --no-cache-dir uv

# Dependency Dateien zuerst kopieren (Docker cache)
COPY pyproject.toml uv.lock ./

# Dependencies installieren
RUN uv pip install --system .

# restlichen Code kopieren
COPY . .

# static files sammeln
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "--keep-alive", "5"]
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
    command: >
      gunicorn config.wsgi:application
      --bind 0.0.0.0:8000
      --workers 3
      --timeout 300

  ollama:
    image: ollama/ollama
    container_name: ai_ollama
    restart: always
    ports:
      - "11434:11434"
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
SECRET_KEY=*prdp2tohumc*-94@n72sm90w+lf%ffcz*b&ro7ak69nalyh

DB_NAME=ai_db
DB_USER=ai_user
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432

# Für den Postgres Container
POSTGRES_DB=ai_db
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=password

OLLAMA_BASE_URL=http://ollama:11434

ALLOWED_HOST=127.0.0.1,localhost,HOST_IP
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://HOST_IP:5173
CSRF_TRUSTED_ORIGINS=http://HOST_IP:HOST_PORT
EOF
```

## Alles sauber starten
```bash
sudo docker compose down -v
sudo docker compose up --build -d
```


## Migration ausführen
```bash
sudo docker exec -it ai_code python manage.py makemigrations
sudo docker exec -it ai_code python manage.py migrate
```

## Model laden
```bash
sudo docker exec -it ai_ollama ollama pull deepseek-coder:6.7b
sudo docker exec -it ai_ollama ollama pull mixtral:8x7b
sudo docker exec -it ai_ollama ollama pull llama3:8b
sudo docker exec -it ai_ollama ollama pull qwen2.5-coder:7b
```

## Prüfe ob Ollama läuft
Ollama besteht aus zwei Schichten:
1. Server Prozess 
2. Installierte Modellgewichte

```bash
ollama list
```
listet alle Model auf


## Teste Ollama Container 
Interner Test
```bash
sudo docker exec -it ai_ollama ollama run deepseek-coder:6.7b
```
Füge das hinzu:
```bash
Write a hello world in Python
```


Mit Ctrl+D beenden.


Terminal Test
```bash
curl -X POST http://192.168.178.98:8003/api/code/generate/ \
-H "Content-Type: application/json" \
-d '{"prompt":"write a python function that adds two numbers","mode":"generate"}'
```

## Logs auslesen
```bash
sudo docker compose logs -f 
```


## Gui aufrufen 
http://127.0.0.1:8000/api/code/
