# AI Code

Self-hosted **AI Code Generation Service** using local LLMs.

Built with:

- **Django / Django REST** – Backend und API
- **PostgreSQL** – Persistente Datenbank
- **Ollama** – Lokale Large Language Models (LLMs)
- **uv** – schneller Python Dependency Manager
- **Docker / Docker Compose** – Containerisierte Infrastruktur

The system allows **local code generation through an API or a simple web GUI**.

---

# Badges

![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![PostgreSQL](https://img.shields.io/badge/database-postgresql-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

**AI Engine**
- Local LLM code generation
- Multi-model support
- Streaming responses

**Supported models**
- deepseek-coder
- mixtral
- llama3
- qwen coder

**API**
- REST API
- JSON requests
- Streaming output

**Infrastructure**
- PostgreSQL database
- Ollama LLM server
- uv dependency management
- Docker deployment

---

## Architektur

```text
Frontend (GUI)
      │
      ▼
Django REST API
      │
      ├── PostgreSQL
      │
      └── Ollama
             │
             └── LLM Models
```

---

## Environment Variablen

**HOST_IP**
- IP address or hostname of the server

**HOST_PORT**
- Port under which the server is reachable

**SECRET_KEY**
- Security key for Django.
- Must be freely chosen and remain secret.

---

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
      - "HOST_PORT:CONTAINER_PORT"
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
SECRET_KEY=CHANGE_ME

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


## Logs auslesen
```bash
sudo docker compose logs -f 
```

## Gui aufrufen 
http://SERVER_IP:HOST_IP/api/code/
