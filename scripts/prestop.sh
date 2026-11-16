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
    # The gunicorn master is the lowest-pid gunicorn process (workers are its
    # children). No pidfile: a stale one in the shared socket volume can stop
    # gunicorn from starting after a container restart.
    PROCESS_ID=""
    for PROC in /proc/[0-9]*
    do
        mapfile -d '' ARGS < "$PROC/cmdline" 2>/dev/null || continue
        if [[ "${ARGS[*]}" == "/app/bin/python"*" /app/bin/gunicorn "* ]]
        then
            PID=${PROC#/proc/}
            if [ -z "$PROCESS_ID" ] || [ "$PID" -lt "$PROCESS_ID" ]
            then
                PROCESS_ID=$PID
            fi
        fi
    done
    SIGNAL=TERM
fi

[ -n "$PROCESS_ID" ] && kill -$SIGNAL $PROCESS_ID

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
