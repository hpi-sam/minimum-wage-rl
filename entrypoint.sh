#!/bin/bash

# Wait for the MySQL container to be ready
#while ! nc -z db 3306; do
#  sleep 1
# done

rm -f economic_simulator/migrations/00*
python manage.py makemigrations
python manage.py migrate

exec gunicorn minimum_wage_rl.wsgi:application --bind 0.0.0.0:8081 --workers 3