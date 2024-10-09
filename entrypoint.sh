python manage.py migrate
echo "########################################"
python manage.py collectstatic --noinput
python manage.py compilemessages
echo "########################################"
gunicorn config.wsgi:application --timeout 3600 --bind 0.0.0.0:9009
