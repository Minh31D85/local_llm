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

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "1600", "--keep-alive", "5"]
