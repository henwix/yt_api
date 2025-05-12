python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
gunicorn core.project.wsgi:application --access-logfile - --error-logfile - --bind 0.0.0.0:8000 --workers=3

# gunicorn core.project.wsgi:application --access-logfile /var/log/django/access.log --error-logfile /var/log/django/error.log --bind 0.0.0.0:8000 --workers=3