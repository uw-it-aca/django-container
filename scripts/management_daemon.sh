#!/bin/bash
set -e

source "/app/bin/activate"

/scripts/management_daemon.py $@
