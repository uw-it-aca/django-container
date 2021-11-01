#!/bin/bash
set -e
set -o noglob

CMD="/scripts/management_command.py"
CMD="/app/tmp/management_command.py"

# quote for space within arguments
for i in "${@:1}"; do
    CMD="$CMD '$i'"
done

source "/app/bin/activate"

bash -c "$CMD"
