# YouTube-like API pet project with Docker Compose, PostgreSQL, Redis, Celery, Celery-Beat, Flower and Makefile.

## Requirements

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)

## How to Use

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your_username/your_repository.git
   cd your_repository

2. **Install all required packages in `Requirements` section.**


### Development Implemented Commands

* `make build` - build application images
* `make app` - up application and database/infrastructure
* `make app-logs` - follow the logs in app container
* `make app-down` - down application and all infrastructure
* `make app-restart` - restart application
* `make db` - up postgresql database
* `make db-down` - down postgresql database
* `make db-logs` - follow the logs in db container
* `make celery-logs` - follow the logs in celery container
* `make beat-logs` - follow the logs in celery-beat container
* `make test` - run application test
* `pre-commit install` - install pre-commit


### Production Implemented Commands

* `make build-prod` - build production application images
* `make app-prod` - up production application and database/infrastructure
* `make app-down-prod` - down production application and all infrastructure
* `make app-restart-prod` - restart production application
* `make nginx-logs-prod` - follow the logs in nginx container
* `make certbot-create-prod` - run certbot to create a new TLS/SSL certificates
* `make certbot-renew-prod` - run certbot to renew existing TLS/SSL certificates
* `make superuser-prod` - create an admin user in production


### Most Used Django Specific Commands

* `make migrations` - make migrations to models
* `make migrate` - apply all made migrations
* `make collectstatic` - collect static
* `make superuser` - create admin user
* `make app-shell` - run django-shell