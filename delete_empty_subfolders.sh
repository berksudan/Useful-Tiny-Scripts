#!/bin/bash

# Change current directory to project directory.
cd "$(dirname "$0")" || exit


# Delete Empty Subdirectories
find . -empty -delete

# Delete This File
rm "$0"