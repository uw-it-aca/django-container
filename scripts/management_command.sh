#!/bin/bash

source "/app/bin/activate"

START_TIME=$(date +%s)

python3 manage.py $@

EXIT_STATUS=$?
EXIT_TIME=$(date +%s)
RUN_TIME=$(( EXIT_TIME - START_TIME ))

if [[ -v PUSHGATEWAY ]]; then
    JOB="$1"
    if [[ -z "$RELEASE_ID" ]]; then
        RELEASE_ID=$(echo -n $HOSTNAME | sed -E 's/-cronjob-.+$//')
    fi

    LABELS="job=\"${JOB}\",instance=\"${RELEASE_ID}\""
    PUSHGATEWAY_PATH="metrics/job/${JOB}/instance/${RELEASE_ID}"

    cat <<EOF | curl --silent --show-error --data-binary @- "http://${PUSHGATEWAY}:9091/${PUSHGATEWAY_PATH}"
# HELP management_command_exit Management command exit code.
# TYPE management_command_exit gauge
management_command_exit{${LABELS}} $EXIT_STATUS
# HELP management_command_finished Time management command last finished.
# TYPE management_command_finished gauge
management_command_finished{${LABELS}} $EXIT_TIME
# HELP management_command_duration Duration of latest management command.
# TYPE management_command_duration gauge
management_command_duration{${LABELS}} $RUN_TIME
EOF
fi
