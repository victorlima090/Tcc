#!/bin/bash

# 5,15,25,35,45,50,55 * * * * export DISPLAY=:0 && sh /home/klenilmar/PythonStuff/captureScriptv2.sh
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

dumpcap -i wlp2s0 -a duration:120 -P -w /home/klenilmar/script_cria_dataset/PythonStuff/captures/youtube/output-$name-home\_$timeSample.pcap

cd /home/klenilmar/script_cria_dataset/PythonStuff/captures/youtube
python /home/klenilmar/script_cria_dataset/featureExtractionv2.py -f /home/klenilmar/script_cria_dataset/PythonStuff/captures/youtube/output-$name-home\_$timeSample.pcap -t 1 -o $name
echo $n
pkill --oldest chrome
pkill chrome
echo "all done!"

