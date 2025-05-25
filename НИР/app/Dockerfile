# Python 3.12 slim основанный образ
FROM python:3.12-slim

# Создадим пользователя non-root для безопасности
RUN useradd -ms /bin/bash ctfuser

WORKDIR /app

# Копируем манифест зависимостей отдельно, чтобы слои кэшировались
COPY requirements.txt ./

# Установка системных пакетов + python зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc build-essential libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем исходники
COPY . .

# Право владения тома с флагами
RUN chown -R ctfuser:ctfuser /opt || true

USER ctfuser

# Flask будет слушать 0.0.0.0:5000
ENV FLASK_APP=app:create_app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

EXPOSE 5000

CMD ["flask", "run"]
