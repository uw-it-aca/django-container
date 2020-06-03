#!/bin/bash
source "/app/bin/activate"

python3 manage.py migrate

if [ -f /scripts/app_deploy.sh ]
then

  . /scripts/app_deploy.sh

fi

if [ "$STATICS"  = "S3" ]
then

  if [ "$ENV" = "dev" ]
  then
    echo "dev"
  fi

  if [ "$ENV" = "prod" ]
  then
    echo "prod"
  fi

fi

# Prepare for readinessProbe
touch /tmp/ready

