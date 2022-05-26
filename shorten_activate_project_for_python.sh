#!/bin/bash

# This program has 2 functionalities
#   1. Shortens path from "~/LONG/PATH/TO/THIS/PARENT_DIR" to "~/.../PARENT_DIR$"
#   2. Activates the virtual environment in python project

CURRENT_PATH="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd -P
)"
cd "$CURRENT_PATH" || exit # Change directory to where bash script resides.

PROMPT_DIRTRIM=1

source "./venv/bin/activate"
