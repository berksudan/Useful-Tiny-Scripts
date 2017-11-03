#!/bin/bash

printf "Let's create a desktop launcher of your app:\n"
printf "What is your app's command?\n"

read app_name
appropriateName=${app_name##*/}

 
touch ~/Desktop/$appropriateName.desktop

echo "Created: ~/Desktop/$appropriateName"

printf "#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec=$app_name
Name[en_US]=$appropriateName
Comment[en_US]="Launcher\ \for\ $appropriateName"
Icon[en_US]=""
Name=$appropriateName
Comment="Launcher\ \for\ $appropriateName"
Icon=""
" | tee  ~/Desktop/$appropriateName.desktop

sudo chmod +x ~/Desktop/$appropriateName.desktop

printf "\nYour app launcher is ready in ~/Desktop\n" 
