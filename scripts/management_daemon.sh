#!/bin/bash
set -e

LOOP_DELAY=15
RE_NUMBER='^[0-9]+$'

while [ $# -gt 0 ]
do
  case "$1" in
    --delay)
      shift
      if [[ $1 =~ $RE_NUMBER ]] ; then
          LOOP_DELAY=$1
      else
          echo "Invalid loop delay: $1"
          exit 1
      fi
      ;;
    --)
      shift
      break
      ;;
    --*)
      echo "Unknown parameter: $1"
      exit 1
      ;;
    *)
      break
      ;;
  esac
  shift
done

source "/app/bin/activate"

while true
do
   python3 manage.py $@
   sleep $LOOP_DELAY
done
