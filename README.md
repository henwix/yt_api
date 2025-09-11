# YT_API - video sharing platform API
YT_API is a video sharing platform API created as a pet project.

<br />

# Shortcuts

* [Project technology stack](#project-technology-stack)
* [Requirements](#requirements)
* [Clone the repository](#clone-the-repository)
* [Development deployment](#development-deployment)
* [Production deployment *with Grafana Monitoring*](#production-deployment-with-grafana-monitoring)
* [Production deployment *without Grafana Monitoring*](#production-deployment-without-grafana-monitoring)
* [Production tips and tricks](#production-tips-and-tricks)
* [Development implemented commands](#development-implemented-commands)
* [Production implemented commands](#production-implemented-commands)
* [Most used Django specific commands](#most-used-django-specific-commands)
* [Environment variables description](#environment-variables-description-from-env-file)

<br />

# Project technology stack

**YT_API uses the following technologies and frameworks:**
* Django and Django Rest Framework for backend and API
* PostgreSQL &ndash; database server
* Redis for caching
* Celery and Celery Beat for task queuing and scheduling
* Nginx &ndash; web and proxy server
* AWS S3 &ndash; cloud storage service
* Certbot for SSL certificates

*<u>Note: the list above contains not all but the key items only</u>*

<br />

# Getting started

## Requirements

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)


## Clone the repository

1. **Clone the repository:**

   ```bash
   git clone https://github.com/henwix/yt_api.git
   cd yt_api
   ```

2. **Install all required packages in [Requirements](#requirements) section.**

## Development deployment

1. Copy `.env.example` to `.env`
2. Make sure you set values for the variables in `.env`:
    * *DJANGO_SETTINGS_FILE* &ndash; to `dev`
    * *SMTP variables block* &ndash; to make SMTP work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *Google reCAPTCHA vars block* &ndash; to make Google reCAPTCHA work
3. Run `make app`
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
5. Open documentation URL (not HTTPS!):
* http://localhost/swagger/
* http://localhost/redoc/


## Production deployment *with Grafana Monitoring*

1. Run `make certbot-create-p` to create SSL certificates using Certbot.
    * Make sure you set the `CERTBOT_DOMAINS` variable in `.env` file before you run Certbot
    * Certbot uses `80` port to accept challenge and create new certificates - make sure the port is available
    * Make sure certificate files are created in the expected directory: `/etc/letsencrypt/live/<domain>`
2. Copy `.env.example` to `.env`
3. Make sure you set values for the variables in `.env`:
    * *NGINX_CONFIG_NAME* &ndash; to `nginx.monitoring.conf`
    * *SECRET_KEY* &ndash; set to a random, secret string
    * *DJANGO_SETTINGS_FILE* &ndash; to `prod`
    * *CERTBOT_EMAIL* &ndash; to your email for Certbot
    * *CERTBOT_DOMAINS* &ndash; to your list of domains
    * *ADMIN_IPV4* and *ADMIN_IPV6* &ndash; to your IP addresses to get access for private endpoints and domains
    * *Application domains block* &ndash; to make Nginx work
    * *SMTP variables block* &ndash; to make SMTP work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *Google reCAPTCHA vars block* &ndash; to make Google reCAPTCHA work
4. Run `make app-monitoring-p` 
5.  Wait until all containers are up:
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

6. Open URLs:
* https://YOUR_API_DOMAIN/swagger/ - Swagger documentation
* https://YOUR_API_DOMAIN/redoc/ - Redoc documentation
* https://YOUR_GRAFANA_DOMAIN/ - Grafana monitoring


## Production deployment *without Grafana Monitoring*

1. Run `make certbot-create-p` to create SSL certificates using Certbot.
    * Make sure you set the `CERTBOT_DOMAINS` variable in `.env` file before you run Certbot
    * Certbot uses `80` port to accept challenge and create new certificates - make sure the port is available
    * Make sure certificate files are created in the expected directory: `/etc/letsencrypt/live/<domain>`
2. Copy `.env.example` to `.env`
3. Change the default values for the variables in `.env`:
    * *NGINX_CONFIG_NAME* &ndash; to `nginx.conf`
    * *SECRET_KEY* &ndash; to a random, secret string
    * *DJANGO_SETTINGS_FILE* &ndash; to `prod`
    * *CERTBOT_EMAIL* &ndash; to your email for Certbot
    * *CERTBOT_DOMAINS* &ndash; to your list of domains
    * *ADMIN_IPV4* and *ADMIN_IPV6* &ndash; to your IP addresses to get access for private endpoints and domains
    * *Application domains block* &ndash; to make Nginx work
    * *SMTP variables block* &ndash; to make SMTP work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *Google reCAPTCHA vars block* &ndash; to make Google reCAPTCHA work
4. Run `make app-p` 
5.  Wait until all containers are up:
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
```

6. Open URLs:
* https://YOUR_API_DOMAIN/swagger/ - Swagger documentation
* https://YOUR_API_DOMAIN/redoc/ - Redoc documentation


## Production tips and tricks

* Use regular (not self signed) SSL certificates
* Do not use default credentials or database settings in production
* Set server names and domains for nginx configuration in *Application domains/hosts* block in `.env` file


<br />

# Application console commands

## Development implemented commands

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
* `make test` - run application tests


## Production implemented commands

* `app-monitoring-p` - build images and up production application with Grafana Monitoring
* `app-monitoring-down-p` - down production application and Grafana Monitoring
* `monitoring` - up Grafana Monitoring without production application
* `monitoring-down` - down Grafana Monitoring without production application
* `monitoring-restart` - restart Grafana Monitoring without production application
* `monitoring-logs` - follow the logs in Grafana Monitoring containers

---

* `make build-p` - build production application images
* `make app-p` - up production application
* `make app-down-p` - down production application
* `make app-restart-p` - restart production application
* `make nginx-logs-p` - follow the logs in nginx container
* `make superuser-p` - create an admin user in production

---

* `make certbot-create-p` - run certbot to create a new TLS/SSL certificates
* `make certbot-renew-p` - run certbot to renew existing TLS/SSL certificates


## Most used Django specific commands

* `make makemigrations` - make migrations to models the Django models
* `make migrate` - apply all created migrations
* `make collectstatic` - collect static
* `make superuser` - create admin user
* `make app-shell` - run django-shell with imported models from the project

<br />

# Environment variables description from `.env` file


| Name                                        | Description                                                              | Notes                                                                                                          | Environment |
| ------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ----------- |
| `SECRET_KEY`                                | Django secret key for security                                           | Generate random string. Example: `openssl rand -hex 50`                                                        | DEV, PROD   |
| `DJANGO_SETTINGS_FILE`                      | Specifies which settings file to use                                     | Controls application settings. Choose between `dev` and `prod`                                                 | DEV, PROD   |
| `DJANGO_ADMIN_PATH`                         | URL path for Django admin panel                                          | Usually `admin`, can be changed for security                                                                   | DEV, PROD   |
| `DJANGO_PORT`                               | The port number on your host machine where you want to access Django     | Default 80. Used in `http://127.0.0.1:DJANGO_PORT/swagger/` or `http://localhost:DJANGO_PORT/swagger/`         | DEV         |
| `POSTGRES_PORT`                             | The port number on your host machine where you want to access PostgreSQL | Default 5432                                                                                                   | DEV         |
| `REDIS_PORT`                                | The port number on your host machine where you want to access Redis      | Default 6379                                                                                                   | DEV         |
| `FLOWER_PORT`                               | The port number on your host machine where you want to access Flower     | Default 5555, can be changed                                                                                   | DEV         |
| `FLOWER_USERNAME`                           | Flower login                                                             | Set manually                                                                                                   | DEV, PROD   |
| `FLOWER_PASSWORD`                           | Flower password                                                          | Set manually                                                                                                   | DEV, PROD   |
| `PGBOUNCER_HOST`                            | Host for pgbouncer (connection pooler)                                   | Usually container name in docker-compose. Example: `pgbouncer`                                                 | PROD        |
| `POSTGRES_HOST`                             | PostgreSQL host                                                          | Usually container name in docker-compose. Example: `postgres`                                                  | DEV, PROD   |
| `POSTGRES_DB`                               | Database name                                                            | Examples: `postgres`, `yt_api`, etc.                                                                           | DEV, PROD   |
| `POSTGRES_USER`                             | Database user                                                            | Usually `postgres`                                                                                             | DEV, PROD   |
| `POSTGRES_PASSWORD`                         | Database user password                                                   | Define your own                                                                                                | DEV, PROD   |
| `AWS_ACCESS_KEY_ID`                         | AWS user access key                                                      | Created in AWS IAM                                                                                             | DEV, PROD   |
| `AWS_SECRET_ACCESS_KEY`                     | AWS user secret key                                                      | Created in AWS IAM                                                                                             | DEV, PROD   |
| `AWS_STORAGE_BUCKET_NAME`                   | Name of S3 bucket for storage                                            | Created in AWS S3                                                                                              | DEV, PROD   |
| `AWS_S3_REGION_NAME`                        | S3 region                                                                | Example: `us-east-1`, `eu-central-1`                                                                           | DEV, PROD   |
| `AWS_S3_VIDEO_BUCKET_PREFIX`                | Prefix for storing videos                                                | Example: `videos/`                                                                                             | DEV, PROD   |
| `AWS_S3_AVATAR_BUCKET_PREFIX`               | Prefix for storing avatars                                               | Example: `channel_avatars/`                                                                                    | DEV, PROD   |
| `AWS_CLOUDFRONT_DOMAIN` | AWS Cloudfront distribution domain | Provided by Cloudfront after distribution creating or can be changed to your custom domain in distribution settings. Example: `1234567890abc.cloudfront.net` | DEV, PROD
| `AWS_CLOUDFRONT_KEY_ID` | ID of the public RSA key that is linked to your distribution. | Obtained in `Cloudfront -> Public keys` and used in presigned URLs to download files. Example: `Z1HBS4DGY52SSS` | DEV, PROD
| `AWS_CLOUDFRONT_KEY` | Private part of the RSA key that is linked to your distribution. | Used in presigned URLs to download files. Example: `-----BEGIN RSA PRIVATE KEY----- GQBoFgGO/QAYlIqR.... -----END RSA PRIVATE KEY-----` | DEV, PROD
| `EMAIL_HOST_USER`                           | SMTP user                                                                | Provided by mail delivery service (Mailgun, Gmail, Sendgrid, etc.)                                             | DEV, PROD   |
| `EMAIL_HOST_PASSWORD`                       | SMTP password                                                            | Provided by mail delivery service (Mailgun, Gmail, Sendgrid, etc.)                                             | DEV, PROD   |
| `DEFAULT_FROM_EMAIL`                        | Default email sender                                                     | Depends on your domain or email registered in mail delivery service. Example: `"YT_API <noreply@example.com>"` | DEV, PROD   |
| `CERTBOT_EMAIL`                             | Email for Certbot registration                                           | Used for certificate expiry notifications                                                                      | PROD        |
| `CERTBOT_DOMAINS`                             | List of domains for which you want to create certificates                                           | Each domain in the list must have the -d flag. Example: `-d first.example.domain -d second.example.domain`                                                                      | PROD        |
| `API_DOMAIN`                                | Domain for API                                                           | Example: `api.example.com`                                                                                     | PROD        |
| `FLOWER_DOMAIN`                             | Domain for Flower                                                        | Example: `flower.example.com`                                                                                  | PROD        |
| `GRAFANA_DOMAIN`                            | Domain for Grafana                                                       | Example: `grafana.example.com`                                                                                 | PROD        |
| `ADMIN_DOMAIN`                              | Domain for Django admin                                                  | Example: `admin.example.com`                                                                                   | PROD        |
| `ADMIN_IPV4`                                | IPv4 addresses for access to private endpoints                           | Set your own IP                                                                                                | PROD        |
| `ADMIN_IPV6`                                | IPv6 addresses for access to private endpoints                           | Set your own IP                                                                                                | PROD        |
| `GRAFANA_ADMIN_USER`                        | Grafana administrator login                                              | Usually `admin`                                                                                                | PROD        |
| `GRAFANA_ADMIN_PASSWORD`                    | Grafana administrator password                                           | Define your own                                                                                                | PROD        |
| `NGINX_CONFIG_NAME`                         | Name of Nginx configuration file                                         | Choose between `nginx.conf` or `nginx.monitoring.conf`                                                         | PROD        |
| `SOCIAL_AUTH_GITHUB_KEY`                    | GitHub OAuth2 key                                                        | Obtained in GitHub OAuth settings                                                                              | DEV, PROD   |
| `SOCIAL_AUTH_GITHUB_SECRET`                 | GitHub OAuth2 secret                                                     | Obtained in GitHub OAuth settings                                                                              | DEV, PROD   |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`             | Google OAuth2 key                                                        | Obtained in Google Cloud Console                                                                               | DEV, PROD   |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`          | Google OAuth2 secret                                                     | Obtained in Google Cloud Console                                                                               | DEV, PROD   |
| `SOCIAL_AUTH_TWITTER_OAUTH2_KEY`            | Twitter OAuth2 key                                                       | Obtained in Twitter Developer Portal                                                                           | DEV, PROD   |
| `SOCIAL_AUTH_TWITTER_OAUTH2_SECRET`         | Twitter OAuth2 secret                                                    | Obtained in Twitter Developer Portal                                                                           | DEV, PROD   |
| `V3_GOOGLE_RECAPTCHA_PRIVATE_KEY`           | Google reCAPTCHA v3 private key                                          | Obtained in Google reCAPTCHA admin console                                                                     | DEV, PROD   |
| `V2_VISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY`   | Google reCAPTCHA v2 (visible) private key                                | Obtained in Google reCAPTCHA admin console                                                                     | DEV, PROD   |
| `V2_INVISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY` | Google reCAPTCHA v2 (invisible) private key                              | Obtained in Google reCAPTCHA admin console                                                                     | DEV, PROD   |


