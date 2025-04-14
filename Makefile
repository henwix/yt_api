DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
MANAGE_PY = python manage.py

APP_CONTAINER = yt-web-dev
APP_CONTAINER_MIDDLE = yt-web-middle
DB_CONTAINER = yt-postgres-dev
DB_SERVICE = postgres
CELERY_CONTAINER = yt-celery-dev
CELERY_BEAT_CONTAINER = yt-celery-beat-dev

APP_DEV_FILE = docker_compose/docker-compose-dev.yml
APP_MIDDLE_FILE = docker_compose/docker-compose-middle.yml


# --DEV--


.PHONY: build-dev
build-dev:
	${DC} -f ${APP_DEV_FILE} build

.PHONY: db-dev
db-dev:
	${DC} -f ${APP_DEV_FILE} up -d ${DB_SERVICE}

.PHONY: db-down-dev
db-down-dev:
	${DC} -f ${APP_DEV_FILE} down ${DB_SERVICE}

.PHONY: db-logs-dev
db-logs-dev:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: db-shell-dev
db-shell-dev:
	${EXEC} ${DB_CONTAINER} psql -U yt-user -d yt

.PHONY: app-dev
app-dev:
	${DC} -f ${APP_DEV_FILE} up -d

.PHONY: app-down-dev
app-down-dev:
	${DC} -f ${APP_DEV_FILE} down

.PHONY: app-restart-dev
app-restart-dev:
	${DC} -f ${APP_DEV_FILE} down && ${DC} -f ${APP_DEV_FILE} up -d

.PHONY: app-logs-dev
app-logs-dev:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-shell-dev
app-shell-dev:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} shell_plus

.PHONY: celery-logs-dev
celery-logs-dev:
	${LOGS} ${CELERY_CONTAINER} -f

.PHONY: beat-logs-dev
beat-logs-dev:
	${LOGS} ${CELERY_BEAT_CONTAINER} -f

.PHONY: makemigrations-dev
makemigrations-dev:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

.PHONY: migrate-dev
migrate-dev:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

.PHONY: superuser-dev
superuser-dev:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser

.PHONY: collectstatic-dev
collectstatic-dev:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} collectstatic

.PHONY: test-dev
test-dev:
	${EXEC} ${APP_CONTAINER} pytest


# --MIDDLE--


.PHONY: build
build:
	${DC} -f ${APP_MIDDLE_FILE} build
.PHONY: app
app:
	${DC} -f ${APP_MIDDLE_FILE} up -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_MIDDLE_FILE} down

.PHONY: app-restart
app-restart:
	${DC} -f ${APP_MIDDLE_FILE} down && ${DC} -f ${APP_MIDDLE_FILE} up -d

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER_MIDDLE} -f

.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER_MIDDLE} ${MANAGE_PY} createsuperuser