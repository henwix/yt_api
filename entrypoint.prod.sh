python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
gunicorn core.project.wsgi:application -c './gunicorn.conf.py'
