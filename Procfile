release: python manage.py makemigrations && python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT core.asgi:application