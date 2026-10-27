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

# Wait for the process to exit (max 20s) rather than sleeping blindly;
# the container normally exits mid-hook, which kubelet reports as FailedPreStopHook
for _ in {1..20}
do
    ALIVE=""
    for PID in $PROCESS_ID
    do
        [ -d "/proc/$PID" ] && ALIVE=1
    done
    [ -z "$ALIVE" ] && break
    sleep 1
done
exit 0
