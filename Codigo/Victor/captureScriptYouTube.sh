#!/bin/bash

# 5,15,25,35,45,50,55 * * * * export DISPLAY=:0 && sh /home/klenilmar/PythonStuff/captureScriptv2.sh
FOLDER_PATH=/home/victor/Documentos/Tcc_Repo/tcc/Codigo/Victor
export DISPLAY=:0
echo $HOME > home.txt
source $HOME/.bashrc
export names=("sony4k", "costaRica", "nasa")
export videos=("oh904_HdkwY", "u3W353OnA3Y", "fVMgnmi2D1w")
export n=$((RANDOM%3))
export timeSample=$(date +"%H-%M_%d-%m-%Y")
export name=$(echo ${names[2]} | sed 's/,$//')
export video=$(echo ${videos[2]} | sed 's/,$//')

google-chrome-stable https://www.youtube.com/embed/$video?autoplay=1 &

dumpcap -i wlp3s0 -a duration:120 -P -w $FOLDER_PATH/captures/youtube/output-$name-home\_$timeSample.pcap

cd $FOLDER_PATH/captures/youtube
python $FOLDER_PATH/featureExtractionv2.py -f $FOLDER_PATH/captures/youtube/output-$name-home\_$timeSample.pcap -t 1 -o $name
echo $n
pkill --oldest chrome
pkill chrome
echo "all done!"

