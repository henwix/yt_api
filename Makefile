DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
MANAGE_PY = python manage.py

ENV = --env-file .env

APP_CONTAINER = yt-web-dev
APP_CONTAINER_MIDDLE = yt-web-middle
DB_CONTAINER = yt-postgres-dev
DB_SERVICE = postgres
DB_CONTAINER_MIDDLE = yt-postgres-middle
CELERY_CONTAINER = yt-celery-dev
CELERY_BEAT_CONTAINER = yt-celery-beat-dev

NGINX_CONTAINER = yt-nginx-middle

APP_DEV_FILE = docker_compose/docker-compose-dev.yml
APP_MIDDLE_FILE = docker_compose/docker-compose-middle.yml
MONITORING_FILE = docker_compose/monitoring.yml
# --DEV--


.PHONY: build
build:
	${DC} -f ${APP_DEV_FILE} ${ENV} build


.PHONY: db
db:
	${DC} -f ${APP_DEV_FILE} ${ENV} up -d ${DB_SERVICE}

.PHONY: db-down
db-down:
	${DC} -f ${APP_DEV_FILE} ${ENV} down ${DB_SERVICE}

.PHONY: db-logs
db-logs:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: db-shell
db-shell:
	${EXEC} ${DB_CONTAINER} psql -U yt-user -d yt


.PHONY: monitoring
monitoring:
	${DC} -f ${MONITORING_FILE} up -d

.PHONY: monitoring-down
monitoring-down:
	${DC} -f ${MONITORING_FILE} down

.PHONY: monitoring-restart
monitoring-restart:
	${DC} -f ${MONITORING_FILE} down && ${DC} -f ${MONITORING_FILE} up -d

.PHONY: monitoring-logs
monitoring-logs:
	${DC} -f ${MONITORING_FILE} ${ENV} logs -f


.PHONY: app
app:
	${DC} -f ${APP_DEV_FILE} ${ENV} up -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_DEV_FILE} ${ENV} down

.PHONY: app-restart
app-restart:
	${DC} -f ${APP_DEV_FILE} ${ENV} down && ${DC} -f ${APP_DEV_FILE} ${ENV} up -d

.PHONY: app-restart-logs
app-restart-logs:
	${DC} -f ${APP_DEV_FILE} ${ENV} down && ${DC} -f ${APP_DEV_FILE} ${ENV} up -d && ${LOGS} ${APP_CONTAINER} -f

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} shell_plus


.PHONY: celery-logs
celery-logs:
	${LOGS} ${CELERY_CONTAINER} -f

.PHONY: beat-logs
beat-logs:
	${LOGS} ${CELERY_BEAT_CONTAINER} -f


.PHONY: makemigrations
makemigrations:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser

.PHONY: collectstatic
collectstatic:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} collectstatic


.PHONY: test
test:
	${EXEC} ${APP_CONTAINER} pytest


# --MIDDLE--


.PHONY: build-middle
build-middle:
	${DC} -f ${APP_MIDDLE_FILE} build
.PHONY: app-middle
app-middle:
	${DC} -f ${APP_MIDDLE_FILE} up -d

.PHONY: app-down-middle
app-down-middle:
	${DC} -f ${APP_MIDDLE_FILE} down

.PHONY: app-restart-middle
app-restart-middle:
	${DC} -f ${APP_MIDDLE_FILE} down && ${DC} -f ${APP_MIDDLE_FILE} up -d

.PHONY: app-logs-middle
app-logs-middle:
	${LOGS} ${APP_CONTAINER_MIDDLE} -f

.PHONY: nginx-logs-middle
nginx-logs-middle:
	${LOGS} ${NGINX_CONTAINER} -f

.PHONY: superuser-middle
superuser-middle:
	${EXEC} ${APP_CONTAINER_MIDDLE} ${MANAGE_PY} createsuperuser

.PHONY: db-logs-middle
db-logs-middle:
	${LOGS} ${DB_CONTAINER_MIDDLE} -f

.PHONY: db-middle
db-middle:
	${DC} -f ${APP_MIDDLE_FILE} ${ENV} up -d ${DB_SERVICE}

.PHONY: db-down-middle
db-down-middle:
	${DC} -f ${APP_MIDDLE_FILE} ${ENV} down ${DB_SERVICE}