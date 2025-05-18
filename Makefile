DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
MANAGE_PY = python manage.py
ENV = --env-file .env

APP_CONTAINER = yt-web-dev
DB_CONTAINER = yt-postgres-dev
DB_SERVICE = postgres
CELERY_CONTAINER = yt-celery-dev
CELERY_BEAT_CONTAINER = yt-celery-beat-dev

APP_DEV_FILE = docker_compose/docker-compose-dev.yml

# -- PRODUCTION VARIABLES --

APP_CONTAINER_PROD = docker_compose-web-1
APP_PROD_FILE = docker_compose/docker-compose-prod.yml
DB_CONTAINER_PROD = yt-postgres-prod
NGINX_CONTAINER = yt-nginx-prod
CERTBOT_CREATE_FILE = docker_compose/docker-compose-certbot-create.yml
CERTBOT_RENEW_FILE = docker_compose/docker-compose-certbot-renew.yml
MONITORING_FILE = docker_compose/monitoring.yml


# -- DEVELOPMENT COMMANDS --


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


# -- PRODUCTION COMMANDS --


.PHONY: certbot-create-prod
certbot-create-prod:
	${DC} -f ${CERTBOT_CREATE_FILE} ${ENV} up && docker container prune -f

.PHONY: certbot-renew-prod
certbot-renew-prod:
	${DC} -f ${CERTBOT_RENEW_FILE} run --rm certbot

.PHONY: build-prod
build-prod:
	${DC} -f ${APP_PROD_FILE} build

.PHONY: app-prod
app-prod:
	${DC} -f ${APP_PROD_FILE} up -d

.PHONY: app-down-prod
app-down-prod:
	${DC} -f ${APP_PROD_FILE} down

.PHONY: app-restart-prod
app-restart-prod:
	${DC} -f ${APP_PROD_FILE} down && ${DC} -f ${APP_PROD_FILE} ${ENV} up --build -d

.PHONY: nginx-logs-prod
nginx-logs-prod:
	${LOGS} ${NGINX_CONTAINER} -f

.PHONY: superuser-prod
superuser-prod:
	${EXEC} ${APP_CONTAINER_PROD} ${MANAGE_PY} createsuperuser
