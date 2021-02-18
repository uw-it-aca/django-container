#!/bin/bash

if [ "$ENV"  = "localdev" ]
then
    PROCESS_ID=$(pgrep -fa "^python manage.py runserver 0:$PORT" | awk '{print $1}')
    SIGNAL=TERM
else
    PROCESS_ID=$(<"/var/run/supervisor/supervisord.pid")
    SIGNAL=TERM
fi

kill -$SIGNAL $PROCESS_ID
sleep 20
exit 0
