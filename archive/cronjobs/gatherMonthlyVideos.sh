#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Collect monthly videos for making into a youtube post
#
# Parameters
#   the month to process in yyyymm format
#
# Consumes
#   MP4s from the archive
#
# Produces
#   a list of MP4s in $DATADIR/videos, synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

if [ $# -lt 1 ] ; then
    yr=$(date --date="1 week ago" +%Y)
    mth=$(date --date="1 week ago" +%m)
    numreq=100
else
    yr=$1
    mth=$2
    numreq=$3
fi
export TMP=/tmp
cd $DATADIR
outdir=$DATADIR/videos/
mkdir -p $outdir > /dev/null 2>&1

tlist=$(python -m reports.findBestMp4s $yr $mth $numreq)
bestvidfile=$outdir/best_${yr}${mth}.txt
if [ -f $bestvidfile ] ; then rm $bestvidfile ; fi 
for t in $tlist 
do 
    echo $t >> $bestvidfile
done

echo "Videos Folder" > $outdir/README.md
echo "" >> $outdir/README.md
echo "This folder contains scripts to download brightest videos for each month from Jan 2022 onwards." >> $outdir/README.md
echo "If you want to download the videos, you can do so as follows:" >> $outdir/README.md
echo "- open a Terminal or Powershell window on your desktop" >> $outdir/README.md
echo "- create a folder to hold the data" >> $outdir/README.md
echo "- cd into this folder, and then run one of the following commands, depending on your platform:" >> $outdir/README.md
echo "for Windows" >> $outdir/README.md
echo "wget https://archive.ukmeteornetwork.co.uk/data/bestvideos/getVideos.ps1 " >> $outdir/README.md
echo "for Linux/MacOS/Unix" >> $outdir/README.md
echo "wget https://archive.ukmeteornetwork.co.uk/data/bestvideos/getVideos.sh " >> $outdir/README.md
echo "" >> $outdir/README.md
echo "Now you can run the downloaded script with a single argument the year+month you want  in YYYYMM format eg" >> $outdir/README.md
echo "./getVideos.sh 202306" >> $outdir/README.md
echo "to retrieve videos for June 2023. The files will be put in a datestamped folder in your current location." >> $outdir/README.md
echo "" >> $outdir/README.md
echo "No special access to AWS is required as downloads are taken from the public website." >> $outdir/README.md

echo "#!/bin/bash" > $outdir/getVideos.sh
echo "wget https://archive.ukmeteornetwork.co.uk/data/bestvideos/best_\$1.txt" >> $outdir/getVideos.sh
echo "mkdir -p \$1 ; cd \$1" >> $outdir/getVideos.sh
echo "cat ../best_\$1.txt | while read i ; do wget https://archive.ukmeteornetwork.co.uk/\$i ; done" >> $outdir/getVideos.sh
echo "cd .." >> $outdir/getVideos.sh
chmod +x $outdir/getVideos.sh

echo "\$1=\$args[0]" > $outdir/getVideos.ps1
echo "wget https://archive.ukmeteornetwork.co.uk/data/bestvideos/best_\$1.txt" >> $outdir/getVideos.ps1
echo "mkdir \$1 ; cd \$1" >> $outdir/getVideos.ps1
echo "foreach(\$line in Get-Content ../best_\$1.txt) { wget https://archive.ukmeteornetwork.co.uk/\$line  }" >> $outdir/getVideos.ps1
echo "cd .." >> $outdir/getVideos.ps1

aws s3 sync $outdir $UKMONSHAREDBUCKET/videos/ --profile ukmonshared --quiet --exclude "*" --include "getVideos*" --include "README*"
aws s3 sync $outdir $OLDUKMONSHAREDBUCKET/videos/ --profile ukmonshared --quiet --exclude "*" --include "getVideos*" --include "README*"

aws s3 sync $outdir $WEBSITEBUCKET/data/bestvideos/ --profile ukmonshared --quiet --include "*.txt"
aws s3 sync $outdir $OLDWEBSITEBUCKET/data/bestvideos/ --profile ukmonshared --quiet --include "*.txt"
