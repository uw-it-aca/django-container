#!/bin/bash

if [ "$ENV"  = "localdev" ]
then
    PROCESS_ID=""
    for PROC in /proc/[0-9]*
    do
        mapfile -d '' ARGS < "$PROC/cmdline" 2>/dev/null || continue
        if [[ "${ARGS[*]}" == "python manage.py runserver 0:$PORT"* ]]
        then
            PROCESS_ID="$PROCESS_ID ${PROC#/proc/}"
        fi
    done
    SIGNAL=TERM
else
    PROCESS_ID=$(<"/var/run/supervisor/supervisord.pid")
    SIGNAL=TERM
fi

kill -$SIGNAL $PROCESS_ID
sleep 20
exit 0
