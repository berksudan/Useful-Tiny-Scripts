#!/bin/bash

# Description:
# This script searches for files in the current directory and its subdirectories,
# excluding those with .webp and .nomedia extensions, and specific directories (.deleteRecord,
# .stversions, .globalTrash, .Links). It also excludes itself from the search results.
# It helps in identifying the files that need cleaning or deletion.
# Ideal for use in directories synced from a phone to a computer for backup purposes.

# Get the name of the script file
script_name=$(basename "$0")

# Define the directories to exclude
excluded_dirs=(
    "sdcard_audiobooks"
    ".deleteRecord"
    ".stversions"
    ".globalTrash"
    ".Links"
    ".thumbnails"
    ".stfolder*"
)

# Build the find command with exclusions
find_cmd="find . -type f ! -name '*.webp' ! -name '.nomedia' ! -name '$script_name'"

for dir in "${excluded_dirs[@]}"; do
    find_cmd+=" ! -path '*/$dir/*'"
done

# Execute the find command and store the result
result=$(eval "$find_cmd")

# Check if any files were found
if [ -z "$result" ]; then
    echo -e "\033[1;96m[SUCCESS] Congratulations, there is no file in the subdirectories!\033[0m"
else
    echo -e "\033[1;31m[WARNING] The following files were found:\033[0m"
    echo "$result"
fi
