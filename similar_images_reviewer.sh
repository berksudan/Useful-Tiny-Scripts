echo_info() {  # Echo in cyan color
    echo -e "\033[0;36m[INFO] $1\033[0m"
}

echo_error() {  # Echo in red color
    echo -e "\e[91m[ERROR] $1\e[0m"
}

echo_debug() {
    echo -e "\e[33m[DEBUG] $1\e[0m"
}

# Get the directory of the bash file and change to that directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR" || exit

echo_info "The files which contain whitespaces are being renamed.."

# Get the list of files with whitespace
files_with_whitespace=()
while IFS= read -d $'\0' -r file; do
    files_with_whitespace+=("$file")
done < <(find . -type f -name "* *" -print0)

# Use files_with_whitespace in a for loop
renamed_files_with_whitespace=()
for file in "${files_with_whitespace[@]}"; do
    new_file=$(echo "$file" | tr ' ' '_')
    mv "$file" "$new_file"
    renamed_files_with_whitespace+=("$new_file")
    echo_debug "Renamed \"$file\" to \"$new_file\"."
done

revert_filenames () {
    # Rename files back to original filenames if they exist
      for file in "${renamed_files_with_whitespace[@]}"; do
        if [ -f "$file" ]; then
            original_file=$(echo "$file" | tr '_' ' ')
            mv "$file" "$original_file"
            echo_debug "Renamed \"$file\" back to \"$original_file\""
        fi
      done
}

echo_info "The files which contain whitespaces has been renamed.."

# The Installation of the package `findimagedupes`
echo_info "Installing 'findimagedupes' if not installed.."
sudo apt install findimagedupes

# Execute the command and store its output in a variable
echo_info "The output of 'findimagedupes' is being retrieved.."
output=$(findimagedupes .)
echo_info "The output of 'findimagedupes' has been successfully retrieved."

# Check if the output is empty
if [ -z "$output" ]; then
  echo_info "No set of similar images have been found."
  revert_filenames
  exit 0
fi

# Get the current directory path
current_path=$(pwd)

# Use sed to remove the current filepath from the output
output=${output//$current_path\//}

# Read each line in the output
count=1 # Initialize a counter
while IFS= read -r line; do
    # Create a directory with the pattern sim_candidates_01, sim_candidates_02, etc.
    mkdir "sim_candidates_0$((count))"

    # Move the files in the current line to the created directory
    # shellcheck disable=SC2086
    mv $line "sim_candidates_0$((count))/"

    # Increment the counter
    count=$((count+1))
done <<< "$output"

# Prompt the user to review the files in the directories `sim_candidates_*`
echo_info "Now, it's time to review the files in the directories 'sim_candidates_*'. After the review is done, please press ENTER."
read -r

# Move all files in directories starting with `sim_candidates_` to the current folder
mv sim_candidates_*/* .

# Delete empty directories starting with "sim_candidates_"
find . -type d -name "sim_candidates_*" -empty -delete

revert_filenames
