#!/bin/bash
set -e

if [ -f /scripts/app_ready.sh ]
then

  . /scripts/app_ready.sh

fi

# if exists, deploy.sh successful
cat /tmp/ready
