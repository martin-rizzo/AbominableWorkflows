#!/bin/bash

# get the directory where this script is located
SCRIPT_DIR=$(dirname "$0")

# construct the full path to the python script
PYTHON_SCRIPT="$SCRIPT_DIR/add-label.py"

# pass all arguments to the python script
python "$PYTHON_SCRIPT" "$@"

