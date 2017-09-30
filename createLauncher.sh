#!/bin/bash

printf "Let's create a desktop launcher of your app:\n"
printf "What is your app's command?\n"

read app_name
touch ~/Desktop/$app_name\ Launcher.desktop

printf "
#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon[en_US]=$app_name
Exec=$app_name
Name[en_US]=$app_name
Comment[en_US]=$app_name
Name=$app_name
Comment=$app_name
Icon=$app_name
" | tee  ~/Desktop/$app_name\ Launcher.desktop

sudo chmod +x ~/Desktop/$app_name\ Launcher.desktop 

printf "\nYour app launcher is ready in ~/Desktop\n" 
