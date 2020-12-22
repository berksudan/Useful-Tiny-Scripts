#!/bin/bash

CURRENT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
RUNNER_SCRIPT="$CURRENT_PATH/run.sh"

while [ ${#var} -eq 0 ]
do
	printf "\033c" # Clear screen	
	echo " _______________"
	echo "|COMMAND OUTPUT |"
	echo "=========================================================="
 	"$RUNNER_SCRIPT"
	echo "=========================================================="
 	read -p "> Press ENTER to run.." var
done

