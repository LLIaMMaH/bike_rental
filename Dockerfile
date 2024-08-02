FROM python:3.12-slim-bullseye

LABEL version="1.0"

ARG CONTAINER_USER=www-user
RUN useradd ${CONTAINER_USER}

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt


COPY . /app/
RUN chown ${CONTAINER_USER}:${CONTAINER_USER} /app

USER ${CONTAINER_USER}

#RUN python3 manage.py collectstatic --noinput --clear
#RUN python3 manage.py makemigrations --no-input
#RUN python3 manage.py migrate --no-input

# Используем, пока тестируем наше приложение только из Dockerfile
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]