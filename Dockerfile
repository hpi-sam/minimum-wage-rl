# set the base image 
FROM python:3.8

COPY requirements.txt .

# Get pip to download and install requirements:
RUN pip install --no-cache-dir -r requirements.txt

#set directoty where CMD will execute 
WORKDIR /usr/src/app

#add project files to the usr/src/app folder
COPY ./minimum_wage_rl /usr/src/app/

# Expose ports
EXPOSE 8001

RUN rm -f db.sqlite3
RUN rm -f economic_simulator/migrations/00*
RUN python manage.py makemigrations
RUN python manage.py migrate


# default command to execute
CMD exec gunicorn minimum_wage_rl.wsgi:application --bind 0.0.0.0:8001 --workers 3