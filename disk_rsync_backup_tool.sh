#!/bin/bash

## How to Use:
##  1. Place this file into your backup disk (the disk you will use as a backup)
##  2. Set DEF_SOURCE_DIR path as your main disk (the disk which contains the files needed to backup)
##  3. Execute this bash file in Linux Terminal.
##  4. Wait until the synchronization process ends. The backup disk may be damaged in case of some interruption during transfer.

DEF_SOURCE_DIR="/media/${USER}/Seagate Expansion Drive/"

read -p "[QUESTION] Is it the source directory: '$DEF_SOURCE_DIR'? [Y/n]: " yn
    case $yn in
        Y|y|"") source_dir=$DEF_SOURCE_DIR;;  
        N|n|*) read -p "Please enter the source directory: " source_dir;;
    esac

echo "[INFO] Source directory: '$source_dir'."


if ! mountpoint -q "${source_dir}"
then
  echo "[ERROR] ${source_dir} is not mounted. Verify this by running: mount -l"
  echo "exiting.."
  exit 1
else
  echo "[INFO] ${source_dir} is mounted."
fi


echo "[INFO] Content of the source directory: '$source_dir'."
ls -la "$source_dir"
read -p "Is it the content of the source directory? [Y/n]: " yn
    case $yn in
        Y|y|"") ;;  
        N|n|*) echo "exiting.."; exit 1 ;;
    esac

backup_bash_filename=`basename "$0"`

echo "[INFO] You will see a DRY RUN out of rsync, in 3 seconds.."
sleep 3
rsync --dry-run -avhP --delete \
    --exclude $backup_bash_filename \
    --exclude '$RECYCLE.BIN/' \
    --exclude 'System Volume Information' \
    --exclude '.Trash-1000' \
    "$source_dir" "./" | grep --color=always "deleting\|$"

echo "-----------------------------"

read -p "Are you satisfied with the DRY RUN and want to do an actual rsync? [y/N]:" yn
    case $yn in
        N|n|"") echo "exiting.."; exit 1 ;;
        Y|y|*) rsync -avhP --delete \
    --exclude $backup_bash_filename \
    --exclude '$RECYCLE.BIN/' \
    --exclude 'System Volume Information' \
    --exclude '.Trash-1000' \
    "$source_dir" "./" | grep --color=always "deleting\|$" ;;
    esac
