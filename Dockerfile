FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

RUN apk add --no-cache postgresql-client build-base postgresql-dev

COPY requirements.txt /app/
RUN pip install -r requirements.txt

RUN adduser --disabled-password yt-user
USER yt-user

EXPOSE 8000

COPY core /app/