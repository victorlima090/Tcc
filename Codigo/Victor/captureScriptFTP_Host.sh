#!/bin/bash

# 5,15,25,35,45,50,55 * * * * export DISPLAY=:0 && sh /home/victor/Documentos/Tcc_Repo/tcc/Codigo/Klenilmar/captureScriptv2.sh
FOLDER_PATH=/home/victor/Documentos/Tcc_Repo/tcc/Codigo/Klenilmar
export DISPLAY=:0
echo $HOME > home.txt
source $HOME/.bashrc
export names=("foxit", "ubuntu")
export ftpUrls=("http://cdn01.foxitsoftware.com/pub/foxit/reader/desktop/linux/2.x/2.4/en_us/FoxitReader2.4.0.14978_Server_x64_enu_Setup.run.tar.gz", "http://releases.ubuntu.com/16.04.2/ubuntu-16.04.2-desktop-amd64.iso?_ga=2.111877062.331754766.1496186396-1595525704.1496186379")
export n=$((RANDOM%2))
export timeSample=$(date +"%H-%M_%d-%m-%Y")
# google-chrome-stable https://www.youtube.com/embed/oh904_HdkwY?autoplay=1 &
export name=$(echo ${names[$n]} | sed 's/,$//')
export ftpUrl=$(echo ${ftpUrls[$n]} | sed 's/,$//')

echo "$name"
echo "$ftpUrl"
google-chrome-stable  $ftpUrl &
dumpcap -i h2-eth0 -a duration:120 -P -w $FOLDER_PATH/captures/output-$name-home\_$timeSample.pcap
cd $FOLDER_PATH
python $FOLDER_PATH/featureExtractionv2.py -f $FOLDER_PATH/captures/output-$name-home\_$timeSample.pcap -t 0 -o $name
echo $n
pkill --oldest chrome
pkill chrome
echo "all done!"

