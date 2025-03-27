FROM python:3.11-alpine

WORKDIR /app/

RUN apk add postgresql-client build-base postgresql-dev

COPY requirements.txt /temp/
RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password yt-user
USER yt-user

EXPOSE 8000

COPY core /app/