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


## Erstelle eine docker compose 

```bash
cat <<'EOF' > docker-compose.yml
version: "3.9"

services:
  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: ai_code
      POSTGRES_USER: ai_user
      POSTGRES_PASSWORD: strongpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: always
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

  web:
    build: .
    restart: always
    command: >
      sh -c "python manage.py migrate &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8003"
    ports:
      - "8003:8003"
    depends_on:
      - db
      - ollama
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
    env_file:
      - .env

volumes:
  postgres_data:
  ollama_data:
EOF
```
