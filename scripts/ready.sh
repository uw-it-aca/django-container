#!/bin/bash
set -e

if [ -f /scripts/app_ready.sh ]
then

  . /scripts/app_ready.sh

fi

if ! [[ -z "$MEMCACHED_SERVER_COUNT" ]]
then

    MEMCACHED_SERVER=${MEMCACHED_SERVER_SPEC//\{\}/0}
    python3 /scripts/memcached_stats.py $MEMCACHED_SERVER

fi

# planted in the filesystem by successful deploy.sh
[ -f /tmp/ready ]
