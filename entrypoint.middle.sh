python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn core.project.wsgi:application --timeout 300 --workers 4 --bind 0.0.0.0:8000