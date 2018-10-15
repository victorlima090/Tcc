#!/bin/bash

# 5,15,25,35,45,50,55 * * * * export DISPLAY=:0 && sh /home/klenilmar/PythonStuff/captureScriptv2.sh
export DISPLAY=:0
echo $HOME > home.txt
source $HOME/.bashrc
export names=("breakingBad", "walkingDead")
export videos=("https://www.netflix.com/watch/70196252?trackId=14183618&tctx=7%2C1%2C25922622-d093-42c6-84a5-2162c41c03ef-9297259", "https://www.netflix.com/watch/70210887?trackId=14170032&tctx=0%2C1%2Cb6a1f2db-f22a-4f37-b512-2273045a1084-59236611")
export n=$((RANDOM%2))
export timeSample=$(date +"%H-%M_%d-%m-%Y")
export name=$(echo ${names[$n]} | sed 's/,$//')
export video=$(echo ${videos[$n]} | sed 's/,$//')

google-chrome-stable $video &


dumpcap -i wlp2s0 -a duration:120 -P -w /home/klenilmar/PythonStuff/captures/netflix/output-$name-home\_$timeSample.pcap
cd /home/klenilmar/PythonStuff/captures/netflix
python /home/klenilmar/featureExtractionv2.py -f /home/klenilmar/PythonStuff/captures/netflix/output-$name-home\_$timeSample.pcap -t 2 -o $name
echo $n
pkill --oldest chrome
pkill chrome
echo "all done!"

