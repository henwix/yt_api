FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

RUN apk add --no-cache postgresql-client build-base postgresql-dev

COPY pyproject.toml /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

RUN adduser --disabled-password yt-user
USER yt-user

EXPOSE 8000

COPY . /app/