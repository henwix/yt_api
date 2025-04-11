python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn core.project.wsgi:application --timeout 3600 --bind 0.0.0.0:8000