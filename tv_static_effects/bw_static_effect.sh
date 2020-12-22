#!/bin/bash

P=(' ' █ ░ ▒ ▓)
while :;do 
	printf "\e[$[RANDOM%LINES+1];$[RANDOM%COLUMNS+1]f${P[$RANDOM%5]}"
done

