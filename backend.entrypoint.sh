#!/bin/sh
set -e

if [ "${DB_ENGINE}" = "postgres" ]; then
  echo "Warte auf PostgreSQL auf $DB_HOST:$DB_PORT..."
  while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
    echo "PostgreSQL ist nicht erreichbar - schlafe 1 Sekunde"
    sleep 1
  done
  echo "PostgreSQL ist bereit - fahre fort..."
fi

python manage.py collectstatic --noinput

# Nur in Dev automatisch Migrationen erzeugen
if [ "${RUN_MAKEMIGRATIONS:-0}" = "1" ]; then
  python manage.py makemigrations
fi

python manage.py migrate --noinput

# Optionaler Superuser nur beim ersten Deploy
if [ "${CREATE_SUPERUSER:-0}" = "1" ]; then
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
if not User.objects.filter(username=u).exists():
    print(f"Creating superuser '{u}'...")
    User.objects.create_superuser(username=u, email=e, password=p)
    print("Superuser created.")
else:
    print(f"Superuser '{u}' already exists.")
EOF
fi

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
