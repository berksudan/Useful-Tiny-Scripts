#!/bin/bash

# Function that escapes special glob characters for use with -path
escape_for_find() {
    local input="$1"
    # Escape backslashes first
    input="${input//\\/\\\\}"
    # Escape glob characters: * ? [ ]
    input="${input//\*/\\*}"
    input="${input//\?/\\?}"
    input="${input//[/\\[}"
    input="${input//]/\\]}"
    echo "$input"
}

# Get the name of the script file
script_name=$(basename "$0")

# Define directories to exclude (without manual escapes)
excluded_dirs=(
    "Audiobooks"
    ".Links"
    ".thumbnails"
    ".sync"
)

# Build the find command as an array
find_args=(find . -type f ! -name '*.webp' ! -name '.trashed-*' ! -name '.nomedia' ! -name "$script_name")

# Append exclusion patterns for each directory, using our escape function.
for dir in "${excluded_dirs[@]}"; do
    escaped_dir=$(escape_for_find "$dir")
    find_args+=( ! -path "*/$escaped_dir/*" )
done

# Execute the find command
result=$("${find_args[@]}")

# Check if any files were found
if [ -z "$result" ]; then
    echo -e "\033[1;96m[SUCCESS] Congratulations, there is no file in the subdirectories!\033[0m"
else
    echo -e "\033[1;31m[WARNING] The following files were found:\033[0m"
    echo "$result"
fi
