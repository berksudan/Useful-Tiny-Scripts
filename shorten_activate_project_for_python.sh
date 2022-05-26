#!/bin/bash

# Functionalities
#   1. Shortens path from "~/LONG/PATH/TO/THIS/PARENT_DIR" to "~/.../PARENT_DIR$"
#   2. Activates the virtual environment in python project

# Usage: "source ./activate_project.sh" OR ". ./activate_project.sh"

CURRENT_PATH="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd -P
)"
cd "$CURRENT_PATH" || exit # Change directory to where bash script resides.

PROMPT_DIRTRIM=1

source "./venv/bin/activate"
