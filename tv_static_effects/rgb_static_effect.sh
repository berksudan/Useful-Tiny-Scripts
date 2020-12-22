#!/bin/bash


P=(' ' █ ░ ▒ ▓)
while :;do
    printf "\e[9$(( ( RANDOM % 7 )  + 1 ))m\e[$[RANDOM%LINES+1];$[RANDOM%COLUMNS+1]f${P[$RANDOM%5]}"
done
