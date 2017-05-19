#!/bin/bash
set -e #exit on errors

#print statements as they are executed
[[ -n $DEBUG_ENTRYPOINT ]] && set -x

case ${1} in
  app:start)
    python run.py
    ;;
  app:help)
    echo "Available options:"
    echo " app:start        - Starts TMR4i Guidelines Explorer (default)"
    echo " [command]        - Execute the specified command, eg. /bin/bash."
    ;;
  *)
    exec "$@"
    ;;
esac

exit 0
