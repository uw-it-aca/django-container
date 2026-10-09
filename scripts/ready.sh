#!/bin/bash
set -e

if [ -f /scripts/app_ready.sh ]
then

  . /scripts/app_ready.sh

fi

if ! [[ -z "$MEMCACHED_SERVER_COUNT" ]]
then

    MEMCACHED_SERVER=$(echo $MEMCACHED_SERVER_SPEC | sed 's/{}/0/g')
    python3 ./memcached_stats.py $MEMCACHED_SERVER

fi

# planted in the filesystem by successful deploy.sh
cat /tmp/ready
