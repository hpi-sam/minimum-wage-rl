# set the base image 
FROM python:3.8

COPY requirements.txt .

# Get pip to download and install requirements:
RUN pip install --no-cache-dir -r requirements.txt

#set directoty where CMD will execute 
WORKDIR /usr/src/app

# Set environment variables for MySQL and Redis
ENV MYSQL_HOST=db
ENV MYSQL_PORT=3306
ENV MYSQL_USER=defaultuser
ENV MYSQL_PASSWORD=defaultpassword
ENV MYSQL_DB=ecodb

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

#add project files to the usr/src/app folder
COPY ./minimum_wage_rl /usr/src/app/

# Expose ports
EXPOSE 8081

# RUN rm -f db.sqlite3
# default command to execute
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
