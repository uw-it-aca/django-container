#!/bin/bash
# Remove any existing httpd data
rm -rf /run/httpd/* /tmp/httpd*

source "/app/bin/activate"



if [ "$DB" = "mysql" ] && [ "$ENV" = "dev" ]
then
  export DATABASE_NAME=`echo $BRANCH | sed 's/-/_/g' `
  mysql -u $DATABASE_USERNAME -p$DATABASE_PASSWORD -h $DATABASE_HOSTNAME --execute="create database $DATABASE_NAME "
fi


if [ "$DB" = "postgres" ] && [ "$ENV" = "dev" ]
then
    export PGPASSWORD=$DATABASE_PASSWORD
    createdb -U $DATABASE_USERNAME -h $DATABASE_HOSTNAME $DATABASE_DB_NAME
fi


if [ -f /scripts/app_start.sh ]
then

  . /scripts/app_start.sh

fi

if [ "$ENV"  = "localdev" ]
then

  python manage.py migrate
  python manage.py runserver 0:$PORT

else

  # Prepare for readinessProbe
  touch /tmp/ready

  if [ "$WEBSERVER" = "nginx" ]
  then

    # Set the port for nginx
    sed  -i 's/${PORT}/'$PORT'/g' /etc/nginx/nginx.conf

    # Start gunicorn and nginx
    exec /app/bin/supervisord -c /etc/supervisor/supervisord.conf -n

  else

    # Start Apache server in foreground
    exec /usr/sbin/apachectl -DFOREGROUND

  fi
fi
