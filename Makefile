DC = docker compose
EXEC = docker compose exec -it
LOGS = docker compose logs
DB_CONTAINER = postgres
CELERY_CONTAINER = celery
CELERY_BEAT_CONTAINER = celery-beat
APP_CONTAINER = web
MANAGE_PY = python manage.py


.PHONY: build
build:
	${DC} build

.PHONY: db
db:
	${DC} up -d ${DB_CONTAINER}

.PHONY: db-down
db-down:
	${DC} down ${DB_CONTAINER}

.PHONY: db-logs
db-logs:
	${LOGS} ${DB_CONTAINER} -f

.PHONY: db-shell
db-shell:
	${EXEC} ${DB_CONTAINER} psql -U yt-user -d yt

.PHONY: app
app:
	${DC} up -d

.PHONY: app-down
app-down:
	${DC} down

.PHONY: app-restart
app-restart:
	${DC} down && ${DC} up -d

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} shell_plus

.PHONY: makemigrations
makemigrations:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser

.PHONY: celery-logs
celery-logs:
	${LOGS} ${CELERY_CONTAINER} -f

.PHONY: beat-logs
beat-logs:
	${LOGS} ${CELERY_BEAT_CONTAINER} -f