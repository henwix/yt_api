# YT_API - video sharing platform API
YT_API - is a video sharing platform API created as a pet project.

<br />

## Introduction

**YT_API uses following technologies and frameworks:**
* Django and Django Rest Framework for backend and API
* PostgreSQL &ndash; database server
* Redis for caching
* Celery and Celery Beat for task queuing and scheduling
* Nginx &ndash; web and proxy server
* AWS S3 &ndash; cloud storage service
* Certbot for SSL certificates

*<u>Note: the list above contains not all but the key items only</u>*

<br />

## Getting started

### Requirements

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)


### How to Use

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your_username/your_repository.git
   cd your_repository

2. **Install all required packages in `Requirements` section.**

 
### Production installation *with Grafana Monitoring*

1. Run `make certbot-create-p` to create ssl certificates using Certbot.
    * Make sure that certificate files found in the directory
2. Copy `.env.template` to `.env`
3. Change the default values for variables in `.env`:
    * *SECRET_KEY* &ndash; to your randomized string
    * *DJANGO_SETTINGS_FILE* &ndash; to `prod`
    * *CERTBOT_EMAIL* &ndash; to your email for Certbot
    * *ADMIN_IPV4* and *ADMIN_IPV6* &ndash; to your ips to get access for private endpoints and domains
    * *SMTP variables block* &ndash; to make SMTP work
    * *Application domains block* &ndash; to make Nginx work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *Google reCAPTCHA vars block* &ndash; to make Google reCAPTCHA work
4. Run `make app-p` 
5.  Wait until all TestY containers are up:
```
$ sudo docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'

NAMES                     PORTS                                                                          STATUS
yt-nginx-prod             0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:443->443/tcp, [::]:443->443/tcp   Up ## seconds
yt-celery-beat-prod       8000/tcp                                                                       Up ## seconds
docker_compose-web-1      8000/tcp                                                                       Up ## seconds
yt-pgbouncer-prod         5432/tcp                                                                       Up ## seconds (healthy)
docker_compose-celery-1   8000/tcp                                                                       Up ## seconds
yt-postgres-prod          5432/tcp                                                                       Up ## seconds (healthy)
yt-celery-exporter-prod   9808/tcp                                                                       Up ## seconds
yt-redis-prod             6379/tcp                                                                       Up ## seconds (healthy)
promtail-prod                                                                                            Up ## seconds
prometheus-prod           9090/tcp                                                                       Up ## seconds
grafana-prod              3000/tcp                                                                       Up ## seconds
loki-prod                 3100/tcp                                                                       Up ## seconds
```

6. Open documentation URL:
* https://YOUR_API_DOMAIN/swagger/
* https://YOUR_API_DOMAIN/redoc/

   
#### Tips and tricks

* Use regular (not self signed) SSL certificates
* Do not use default settings for database, other services and credentials
* Set server names for nginx configuration by *Application domains/hosts* block in `.env` file

### Production installation *with Grafana Monitoring*

---

### Development deployment

1. Copy `.env.example` to `.env`
2. Run `make app`
4. Wait until all containers are up:
```
$ sudo docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'

NAMES                PORTS                                     STATUS
yt-web-dev           0.0.0.0:80->8000/tcp, [::]:80->8000/tcp   Up ## seconds
yt-celery-dev        8000/tcp                                  Up ## seconds
yt-celery-beat-dev   8000/tcp                                  Up ## seconds
yt-redis-dev         6379/tcp                                  Up ## seconds (healthy)
yt-postgres-dev      5432/tcp                                  Up ## seconds (healthy)
```
4. Open documentation URL (not HTTPS!):
* http://localhost/swagger/
* http://localhost/redoc/

<br />

## Application console commands

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

* `make build-p` - build production application images
* `make app-p` - up production application and database/infrastructure
* `make app-down-p` - down production application and all infrastructure
* `make app-restart-p` - restart production application
* `make nginx-logs-p` - follow the logs in nginx container
* `make certbot-create-p` - run certbot to create a new TLS/SSL certificates
* `make certbot-renew-p` - run certbot to renew existing TLS/SSL certificates
* `make superuser-p` - create an admin user in production


### Most Used Django Specific Commands

* `make migrations` - make migrations to models
* `make migrate` - apply all made migrations
* `make collectstatic` - collect static
* `make superuser` - create admin user
* `make app-shell` - run django-shell

### ENV variables description

* `SECRET_KEY` - ***NECESSARY*** - Django secret key