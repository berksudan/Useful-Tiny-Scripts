echo_info() {  # Echo in cyan color
    echo -e "\033[0;36m[INFO] $1\033[0m"
}

echo_error() {  # Echo in red color
    echo -e "\e[91m[ERROR] $1\e[0m"
}

# Get the directory of the bash file and change to that directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if any files in the current directory contain empty space
files_with_spaces=$(find . -type f -name "* *" -exec echo {} \;)

if [ -n "$files_with_spaces" ]; then
    echo_error "The following files exist and cannot contain empty space; please rename them before continuing: $files_with_spaces"
    exit 1
fi

# The Installation of the package `findimagedupes`
echo_info "Installing 'findimagedupes' if not installed.."
sudo apt install findimagedupes

# Execute the command and store its output in a variable
echo_info "The output of 'findimagedupes' is being retrieved.."
# output=$(findimagedupes .  2>/dev/null)
output=$(findimagedupes .)
echo_info "The output of 'findimagedupes' has been successfully retrieved."

# Get the current directory path
current_path=$(pwd)

# Use sed to remove the current filepath from the output
output=$(echo "$output" | sed "s|$current_path/||g")

# Initialize a counter
count=1

# Read each line in the output
while IFS= read -r line; do
    # Create a directory with the pattern sim_candidates_01, sim_candidates_02, etc.
    mkdir "sim_candidates_0$((count))"
    
    # Move the files in the current line to the created directory
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
