#!/bin/bash
set -e

source "/app/bin/activate"

python3 manage.py $@
