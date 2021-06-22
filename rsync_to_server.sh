#!/bin/bash

parse_target_arguments() {
  while getopts u:h:d: option; do
    case "${option}" in
    u) TARGET_USER="${OPTARG}" ;;
    h) TARGET_HOST="${OPTARG}" ;;
    d) TARGET_PARENT_DIR="${OPTARG}" ;;
    *) echo "Wrong input, exiting.." && exit ;;
    esac
  done
  if [ -z "$TARGET_USER" ] || [ -z "$TARGET_HOST" ] || [ -z "$TARGET_PARENT_DIR" ]; then
    {
      echo "Error: All parameters must be filled. Parameters: (-u) TARGET_USER, (-h) TARGET_HOST, (-d) TARGET_PARENT_DIR."
      echo 'Example Usage: <<./rsync_to_server.sh -u "ambari" -h "vsansbdtool01.dsans.int" -d "~/mock_dev">>'
      echo "exiting.." && exit
    }
  fi
}

merge_array() { # [USAGES]: $(merge_array AN_ARRAY_NAME) OR $(merge_array AN_ARRAY_NAME PREPOSITION_NAME)
  local -n an_array=$1
  local preposition_name=$2
  merged_string=""

  for i in "${an_array[@]}"; do merged_string="$merged_string $preposition_name$i"; done
  echo "$merged_string"
}

beautify_array_values() { # [USAGE]: $(beautify_array_values "${AN_ARRAY_NAME[*]}")
  echo "[\"$*\"]" | awk -v OFS="\", \"" '$1=$1'
}

get_current_path() { # [USAGE]: $(get_current_path)
  cd "$(dirname "$0")" || exit
  pwd -P
}

PROJECT_PATH="$(get_current_path)"
PROJECT_NAME="${PROJECT_PATH##*/}"

parse_target_arguments "$@"

SOURCE_PATH="$PROJECT_PATH/"
TARGET_PATH="$TARGET_USER@$TARGET_HOST:$TARGET_PARENT_DIR/$PROJECT_NAME"

EXCLUDED_FILES=('venv' '.idea' 'auto_rsync.sh' 'auto_run.sh' '__pycache__')
RSYNC_PARAMETERS=('--archive' '--no-owner' '--no-group' '--delete' '--progress' '--rsh "ssh"')

printf "[INFO] Excluded Files: " && beautify_array_values "${EXCLUDED_FILES[*]}"
printf "[INFO] Rsync Files: " && beautify_array_values "${RSYNC_PARAMETERS[*]}"

MERGED_EXCLUDED_FILES=$(merge_array EXCLUDED_FILES "--exclude ")
MERGED_RSYNC_PARAMETERS=$(merge_array RSYNC_PARAMETERS)

echo "[INFO] Executing:" "rsync $MERGED_RSYNC_PARAMETERS $MERGED_EXCLUDED_FILES $SOURCE_PATH $TARGET_PATH"
rsync $MERGED_RSYNC_PARAMETERS $MERGED_EXCLUDED_FILES $SOURCE_PATH $TARGET_PATH
