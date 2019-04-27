#!/bin/bash
# Remove any existing httpd data
rm -rf /run/httpd/* /tmp/httpd*

source "/app/bin/activate"



if [ "$DB" = "mysql" ] && [ "$ENV" = "dev" ]
then
  export DATABASE_NAME=`echo $BRANCH | sed 's/-/_/g' `
  mysql -u $DATABASE_USERNAME -p$DATABASE_PASSWORD -h $DATABASE_HOSTNAME --execute="create database $DATABASE_NAME "
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

  # Start Apache server in foreground
  exec /usr/sbin/apachectl -DFOREGROUND

fi
