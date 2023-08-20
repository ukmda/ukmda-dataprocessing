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

if [ ! -f $outdir/README.md ] ; then 
    echo "Videos Folder" > $outdir/README.md
    echo "" >> $outdir/README.md
    echo "This folder contains lists of the brightest videos for each month." >> $outdir/README.md
    echo "If you want to download them, first download getVideos.sh (for Linux or MacOS) or " >> $outdir/README.md
    echo "getVideos.ps1 (for Windows 10 or later). Then run the script with a single argument " >> $outdir/README.md
    echo "which is the year+month you want eg" >> $outdir/README.md
    echo "./getVideos.sh 202306" >> $outdir/README.md
    echo "to retrieve videos for June 2026. The files will be put in a datestamped folder" >> $outdir/README.md

    echo "#!/bin/bash" > $outdir/getVideos.sh
    echo "aws s3 cp s3://ukmon-shared/videos/best_\$ym.txt ." >> $outdir/getVideos.sh
    echo "mkdir -p \$1 ; cd \$1" >> $outdir/getVideos.sh
    echo "cat ../best_\$1.txt | while read i ; do wget https://archive.ukmeteornetwork.co.uk/\$i ; done" >> $outdir/getVideos.sh
    echo "cd .." >> $outdir/getVideos.sh
    chmod +x $outdir/getVideos.sh

    echo "\$1=\$args[0]" > $outdir/getVideos.ps1
    echo "aws s3 cp s3://ukmon-shared/videos/best_\$1.txt ." >> $outdir/getVideos.ps1
    echo "mkdir \$1 ; cd \$1" >> $outdir/getVideos.ps1
    echo "foreach(\$line in Get-Content ../best_\$1.txt) { wget https://archive.ukmeteornetwork.co.uk/\$line  }" >> $outdir/getVideos.ps1
    echo "cd .." >> $outdir/getVideos.ps1

fi

aws s3 sync $outdir $UKMONSHAREDBUCKET/videos/ --profile ukmonshared --quiet
aws s3 cp $outdir $OLDUKMONSHAREDBUCKET/videos/ --profile ukmonshared --quiet
