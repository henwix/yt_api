# YT_API - video sharing platform API

YT_API is a video sharing platform API created as a pet project.

<br />

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/194ca13b-0009-4082-a5b2-fb097b052992" />

## Shortcuts

* [Project technology stack and Features](#project-technology-stack-and-features)
* [Requirements](#requirements)
* [Clone the repository](#clone-the-repository)
* [Development deployment](#development-deployment)
* [Production deployment *with Grafana Monitoring*](#production-deployment-with-grafana-monitoring)
* [Production deployment *without Grafana Monitoring*](#production-deployment-without-grafana-monitoring)
* [Production tips and tricks](#production-tips-and-tricks)
* [Development commands](#development-commands)
* [Production commands](#production-commands)
* [Most used Django specific commands](#most-used-django-specific-commands)
* [Environment variables description](#environment-variables-description-for-env-file)

<br />

## Project technology stack and Features

* 🐍 [Django](https://www.djangoproject.com/) and [Django Rest Framework](https://www.django-rest-framework.org/) for backend and API.
* 📜 [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/readme.html) for API documentation.
* 🐘 [PostgreSQL](https://www.postgresql.org/) &ndash; SQL database.
* 🚀 [Redis](https://redis.io/) for caching.
* 📝 [Celery](https://github.com/celery/celery) and [Celery Beat](https://github.com/celery/django-celery-beat) for task queuing and scheduling.
* 🖧 [Nginx](https://nginx.org/en/) &ndash; web and proxy server.
* 🐳 [Docker Compose](https://www.docker.com/) for development and production.
* ☁️ [AWS S3](https://aws.amazon.com/s3/) && [CloudFront](https://aws.amazon.com/cloudfront/) &ndash; cloud storage service and CDN.
* 💸 [Stripe](https://stripe.com/) for payments.
* 🤖 [Certbot](https://certbot.eff.org/) for SSL certificates.
* ✅ [Pytest](https://docs.pytest.org/en/stable/) for testing.
* 📫 Email based password and username recovery.
* 🔒 Secure password hashing by default.
* 🔑 JWT (JSON Web Token) authentication.

*<u>Note: the list above contains not all but the key items only</u>*

<br />

## Getting started

### Requirements

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)
* [GNU Make](https://www.gnu.org/software/make/)

### Clone the repository

1. **Clone the repository:**

   ```bash
   git clone https://github.com/henwix/yt_api.git
   cd yt_api
   ```

2. **Install all required packages in [Requirements](#requirements) section.**

### Development deployment

1. Copy `.env.example` to `.env`
2. Make sure you set values for the variables in `.env`:
    * *DJANGO_SETTINGS_FILE* &ndash; to `dev`
    * *SMTP & Email vars block* &ndash; to make SMTP work (not required for development)
    * *OAuth2 vars block* &ndash; to make OAuth2 work (not required for development)
    * *reCAPTCHA vars block* &ndash; to make reCAPTCHA work (not required for development)
    * *AWS S3 & CloudFront vars block* &ndash; to make files uploading and S3 bucket work (not required for development)
    * *Stripe vars block* &ndash; to make payments work (not required for development)
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

5. Create database migrations and apply them:

```
make makemigrations
make migrate
```

6. Open documentation URL (not HTTPS!):

* <http://localhost/swagger/>
* <http://localhost/redoc/>

### Production deployment *with Grafana Monitoring*

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
    * *SSL & Domains block* &ndash; to make Nginx work
    * *SMTP & Email vars block* &ndash; to make SMTP work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *reCAPTCHA vars block* &ndash; to make reCAPTCHA work
    * *AWS S3 & CloudFront vars block* &ndash; to make files uploading and S3 bucket work
    * *Stripe vars block* &ndash; to make payments work
4. Run `make app-monitoring-p`
5. Wait until all containers are up:

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

### Production deployment *without Grafana Monitoring*

1. Run `make certbot-create-p` to create SSL certificates using Certbot.
    * Make sure you set the `CERTBOT_DOMAINS` variable in `.env` file before you run Certbot
    * Certbot uses `80` port to accept challenge and create new certificates - make sure the port is available
    * Make sure certificate files are created in the expected directory: `/etc/letsencrypt/live/<domain>`
2. Copy `.env.example` to `.env`
3. Make sure you set values for the variables in `.env`:
    * *NGINX_CONFIG_NAME* &ndash; to `nginx.conf`
    * *SECRET_KEY* &ndash; set to a random, secret string
    * *DJANGO_SETTINGS_FILE* &ndash; to `prod`
    * *CERTBOT_EMAIL* &ndash; to your email for Certbot
    * *CERTBOT_DOMAINS* &ndash; to your list of domains
    * *ADMIN_IPV4* and *ADMIN_IPV6* &ndash; to your IP addresses to get access for private endpoints and domains
    * *SSL & Domains block* &ndash; to make Nginx work
    * *SMTP & Email vars block* &ndash; to make SMTP work
    * *OAuth2 vars block* &ndash; to make OAuth2 work
    * *reCAPTCHA vars block* &ndash; to make reCAPTCHA work
    * *AWS S3 & CloudFront vars block* &ndash; to make files uploading and S3 bucket work
    * *Stripe vars block* &ndash; to make payments work
4. Run `make app-p`
5. Wait until all containers are up:

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

### Production tips and tricks

* Use regular (not self signed) SSL certificates
* Do not use default credentials or database settings in production
* Set server names and domains for nginx configuration in *SSL & Domains* block in `.env` file

<br />

## Application console commands

### Development commands

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

### Production commands

* `make app-p` - build images and up production application
* `make app-down-p` - down production application
* `make app-restart-p` - restart production application
* `make nginx-logs-p` - follow the logs in nginx container
* `make superuser-p` - create an admin user in production

---

* `make app-monitoring-p` - build images and up production application with Grafana Monitoring
* `make app-monitoring-down-p` - down production application and Grafana Monitoring
* `make monitoring` - up Grafana Monitoring without production application
* `make monitoring-down` - down Grafana Monitoring without production application
* `make monitoring-restart` - restart Grafana Monitoring without production application
* `make monitoring-logs` - follow the logs in Grafana Monitoring containers

---

* `make certbot-create-p` - run certbot to create a new TLS/SSL certificates
* `make certbot-renew-p` - run certbot to renew existing TLS/SSL certificates

### Most used Django specific commands

* `make makemigrations` - make migrations to models the Django models
* `make migrate` - apply all created migrations
* `make collectstatic` - collect static
* `make superuser` - create admin user
* `make app-shell` - run django-shell with imported models from the project

<br />

## Environment variables description for `.env` file

#### ⚙️ Django

* `SECRET_KEY`: (default: `"12345"`) The Django secret key for cryptographic signing and security. Can be generated using `openssl rand -hex 50`. [Docs](https://docs.djangoproject.com/en/stable/ref/settings/#secret-key). *Environment — DEV, PROD*
* `DJANGO_SETTINGS_FILE`: (default: `"dev"`) Specifies which Django settings file to use (`dev` or `prod`). Controls Django settings and environment-specific behavior. *Environment — DEV, PROD*
* `DJANGO_ADMIN_PATH`: (default: `"admin"`) The URL path for the Django admin panel. Usually `admin`, but can be changed for better security. *Environment — DEV, PROD*
* `LOGGING_LEVEL`: (default: `"INFO"`) Logging level for Django (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). *Environment — DEV, PROD*

#### 🐳 Docker & Deployment

* `DJANGO_PORT`: (default: `"80"`) The port on your host where Django is accessible. *Environment — DEV*
* `POSTGRES_PORT`: (default: `"5432"`) The port on your host for PostgreSQL. *Environment — DEV*
* `REDIS_PORT`: (default: `"6379"`) The port on your host for Redis. *Environment — DEV*
* `FLOWER_PORT`: (default: `"5656"`) The port on your host for Flower. *Environment — DEV*
* `NGINX_CONFIG_NAME`: (default: `"nginx.conf"`) Name of Nginx config file (`nginx.conf` or `nginx.monitoring.conf`). *Environment — PROD*

#### 🐘 PostgreSQL & PgBouncer

* `PGBOUNCER_HOST`: (default: `"pgbouncer"`) Host for PgBouncer connection pooler. *Environment — PROD*
* `POSTGRES_HOST`: (default: `"postgres"`) Host for PostgreSQL. *Environment — DEV, PROD*
* `POSTGRES_DB`: (default: `"postgres"`) Name of the PostgreSQL database. *Environment — DEV, PROD*
* `POSTGRES_USER`: (default: `"postgres"`) Username for PostgreSQL. *Environment — DEV, PROD*
* `POSTGRES_PASSWORD`: (default: `"postgres"`) Password for PostgreSQL user. Set manually for better security. *Environment — DEV, PROD*

#### 📫 SMTP & Email

* `EMAIL_HOST_USER`: (default: `""`) SMTP user (Mailgun, Gmail, Sendgrid, etc.). *Environment — DEV, PROD*
* `EMAIL_HOST_PASSWORD`: (default: `""`) SMTP password. *Environment — DEV, PROD*
* `DEFAULT_FROM_EMAIL`: (default: `"example <noreply@example.com>"`) Default email sender (e.g., `"YT_API <noreply@example.com>"`). *Environment — DEV, PROD*
* `AUTH_SEND_ACTIVATION_EMAIL`: (default: `"False"`) Whether to send activation emails (`True` keeps users inactive and sends an email). *Environment — DEV, PROD*

#### ☁️ AWS & CloudFront

* `AWS_ACCESS_KEY_ID`: (default: `""`) AWS IAM user access key. Created in AWS IAM. [Docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html). *Environment — DEV, PROD*
* `AWS_SECRET_ACCESS_KEY`: (default: `""`) AWS IAM user secret key. Created in AWS IAM. *Environment — DEV, PROD*
* `AWS_STORAGE_BUCKET_NAME`: (default: `""`) AWS S3 bucket name for file storage. [Docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html). *Environment — DEV, PROD*
* `AWS_S3_REGION_NAME`: (default: `""`) AWS S3 bucket region (e.g., `eu-central-1`). *Environment — DEV, PROD*
* `AWS_S3_VIDEO_BUCKET_PREFIX`: (default: `"videos/"`) Prefix for storing uploaded videos. *Environment — DEV, PROD*
* `AWS_S3_AVATAR_BUCKET_PREFIX`: (default: `"channel_avatars/"`) Prefix for storing avatars. *Environment — DEV, PROD*
* `AWS_CLOUDFRONT_DOMAIN`: (default: `""`) AWS CloudFront distribution domain (e.g., `1234567890abc.cloudfront.net`). *Environment — DEV, PROD*
* `AWS_CLOUDFRONT_KEY_ID`: (default: `""`) ID of the public RSA key linked to the CloudFront distribution. *Environment — DEV, PROD*
* `AWS_CLOUDFRONT_KEY`: (default: `""`) Private RSA key for CloudFront presigned URLs. *Environment — DEV, PROD*

#### 🌐 Frontend URLs

* `FRONTEND_PROTOCOL`: (default: `"http"`) Protocol used to generate frontend links (`http` or `https`). *Environment — DEV, PROD*
* `FRONTEND_DOMAIN`: (default: `"example.com"`) Domain of the frontend application, used to build full URLs in redirects, API responses, and emails. *Environment — DEV, PROD*
* `FRONTEND_PASSWORD_RESET_URI`: (default: `"/auth/password_reset_confirm/"`) URI for password reset confirmation page. *Environment — DEV, PROD*
* `FRONTEND_USERNAME_RESET_URI`: (default: `"/auth/username_reset_confirm/"`) URI for username reset confirmation page. *Environment — DEV, PROD*
* `FRONTEND_ACTIVATE_URI`: (default: `"/auth/activate/"`) URI for user account activation page. *Environment — DEV, PROD*

#### 🔐 SSL & Domains

* `CERTBOT_EMAIL`: (default: `""`) Email used for Certbot SSL registration and notifications. [Docs](https://certbot.eff.org/). *Environment — PROD*
* `CERTBOT_DOMAINS`: (default: `""`) Domains for SSL certificate creation (e.g., `-d api.example.com -d admin.example.com`). *Environment — PROD*
* `API_DOMAIN`: (default: `""`) Domain for API (e.g., `api.example.com`). *Environment — PROD*
* `FLOWER_DOMAIN`: (default: `""`) Domain for Flower (e.g., `flower.example.com`). *Environment — PROD*
* `GRAFANA_DOMAIN`: (default: `""`) Domain for Grafana (e.g., `grafana.example.com`). *Environment — PROD*
* `ADMIN_DOMAIN`: (default: `""`) Domain for Django admin (e.g., `admin.example.com`). *Environment — PROD*
* `ADMIN_IPV4`: (default: `""`) Whitelisted IPv4 addresses for private admin endpoints. *Environment — PROD*
* `ADMIN_IPV6`: (default: `""`) Whitelisted IPv6 addresses for private admin endpoints. *Environment — PROD*

#### 🔑 OAuth2

* `SOCIAL_AUTH_GITHUB_KEY`: (default: `""`) GitHub OAuth2 client key. [Docs](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app). *Environment — DEV, PROD*
* `SOCIAL_AUTH_GITHUB_SECRET`: (default: `""`) GitHub OAuth2 client secret. *Environment — DEV, PROD*
* `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`: (default: `""`) Google OAuth2 client key. [Docs](https://developers.google.com/identity/protocols/oauth2). *Environment — DEV, PROD*
* `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`: (default: `""`) Google OAuth2 client secret. *Environment — DEV, PROD*
* `SOCIAL_AUTH_TWITTER_OAUTH2_KEY`: (default: `""`) Twitter OAuth2 key. [Docs](https://docs.x.com/fundamentals/developer-apps). *Environment — DEV, PROD*
* `SOCIAL_AUTH_TWITTER_OAUTH2_SECRET`: (default: `""`) Twitter OAuth2 secret. *Environment — DEV, PROD*

#### 🧩 reCAPTCHA

* `CAPTCHA_VALIDATION_ENABLED`: (default: `"True"`) Enables or disables CAPTCHA validation (`True` or `False`). Useful for disabling CAPTCHA in local/dev environments. *Environment — DEV, PROD*
* `V3_GOOGLE_RECAPTCHA_PRIVATE_KEY`: (default: `""`) Google reCAPTCHA v3 secret key. [Docs](https://developers.google.com/recaptcha/docs/v3). *Environment — DEV, PROD*
* `V2_VISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY`: (default: `""`) Google reCAPTCHA v2 visible secret key. [Docs](https://developers.google.com/recaptcha/docs/v2) *Environment — DEV, PROD*
* `V2_INVISIBLE_GOOGLE_RECAPTCHA_PRIVATE_KEY`: (default: `""`) Google reCAPTCHA v2 invisible secret key. [Docs](https://developers.google.com/recaptcha/docs/v2) *Environment — DEV, PROD*

#### 💸 Stripe

* `STRIPE_SECRET_KEY`: (default: `""`) Secret API key for Stripe used to perform secure operations like creating customers, subscriptions, or webhooks. Obtain from Stripe Dashboard → Developers → API keys. [Docs](https://stripe.com/docs/keys). *Environment — DEV, PROD*
* `STRIPE_PUBLISHABLE_KEY`: (default: `""`) Public API key for Stripe used on the frontend to initialize payments. Obtain from Stripe Dashboard → Developers → API keys. *Environment — DEV, PROD*
* `STRIPE_WEBHOOK_KEY`: (default: `""`) Signing secret used to verify incoming Stripe webhook events for authenticity. Obtain from Stripe Dashboard → Developers → Webhooks. *Environment — DEV, PROD*
* `STRIPE_SUB_PRICE_PRO`: (default: `""`) ID of the Stripe Price object for the “Pro” subscription tier. Obtain from Stripe Dashboard → Products → Pricing. *Environment — DEV, PROD*
* `STRIPE_SUB_PRICE_PREMIUM`: (default: `""`) ID of the Stripe Price object for the “Premium” subscription tier. Obtain from Stripe Dashboard → Products → Pricing. *Environment — DEV, PROD*

#### 📊 Monitoring

* `GRAFANA_ADMIN_USER`: (default: `"admin"`) Grafana admin username. *Environment — PROD*
* `GRAFANA_ADMIN_PASSWORD`: (default: `"password"`) Grafana admin password. *Environment — PROD*
* `FLOWER_USERNAME`: (default: `"admin"`) Username for Flower monitoring dashboard. Used for basic HTTP authentication. *Environment — DEV, PROD*
* `FLOWER_PASSWORD`: (default: `"password"`) Password for Flower monitoring dashboard. Set manually for better security. *Environment — DEV, PROD*
