source "/app/bin/activate"

python3 manage.py migrate


if [ "$STATICS"  = "S3"]
then

  if [ "$ENV" = "dev"]
  then

  fi

  if [ "ENV" = "prod"]
  then

  fi

fi




if [ -f /scripts/app_deploy.sh ]
then

  . /scripts/app_deploy.sh

fi