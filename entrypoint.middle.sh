python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
# gunicorn core.project.wsgi:application --timeout 300 --bind 0.0.0.0:8000
gunicorn core.project.wsgi:application --bind 0.0.0.0:8000