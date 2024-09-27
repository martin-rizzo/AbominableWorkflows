#!/usr/bin/env bash

# get the script's name without the .sh extension
SCRIPT_NAME=$(basename "${BASH_SOURCE[0]}" .sh)

# get the absolute path of the directory containing this script
SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")

# construct the full path to the python script
PYTHON_SCRIPT="$SCRIPT_DIR/${SCRIPT_NAME%%-*}.py"

# check if the python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found." >&2
    exit 1
fi

# execute the python script, passing all arguments to it
python "$PYTHON_SCRIPT" "$@"

