FROM python:3.12
MAINTAINER Weinmaier Andrew
LABEL version="0.42"

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование скриптов
COPY cgi-bin/ /app/cgi-bin/

# Установка пакетов для работы с PostgreSQL и Apache
RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev \
    apache2 \
    libapache2-mod-wsgi-py3

# Установка разрешений на выполнение скриптов
RUN chmod +x /app/cgi-bin/parser_1.py

# Конфигурация Apache
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Запуск Apache
CMD ["apachectl", "-D", "FOREGROUND"]


