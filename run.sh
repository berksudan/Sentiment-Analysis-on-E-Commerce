#!/bin/bash

# Change current directory to the project directory.
CURRENT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

# Paths of Python 3 and main module.
PYTHON_BIN=python3
PYTHON_MAIN=$CURRENT_PATH/main.py

# Run the program.
$PYTHON_BIN $PYTHON_MAIN