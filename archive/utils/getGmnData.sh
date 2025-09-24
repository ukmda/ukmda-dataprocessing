#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd $DATADIR/gmndata

y1=$(date +%Y)
y2=$(date +%Y --date 'yesterday')
rsync -vtz gmn.uwo.ca:/srv/meteor-ro/rms/gmn/extracted_data/auto_output/traj_summary_data/*$y1.txt . --exclude traj_summary_all.txt
if [ "$ym1" != "$ym2" ] ; then 
    rsync -vtz gmn.uwo.ca:/srv/meteor-ro/rms/gmn/extracted_data/auto_output/traj_summary_data/*$y2.txt . --exclude traj_summary_all.txt
fi
ym1=$(date +%Y%m)
ym2=$(date +%Y%m --date 'yesterday')
rsync -vtz gmn.uwo.ca:/srv/meteor-ro/rms/gmn/extracted_data/auto_output/traj_summary_data/monthly/*${ym1}.txt ./monthly --exclude traj_summary_all.txt
if [ "$ym1" != "$ym2" ] ; then 
    rsync -vtz gmn.uwo.ca:/srv/meteor-ro/rms/gmn/extracted_data/auto_output/traj_summary_data/monthly/*${ym2}.txt ./monthly --exclude traj_summary_all.txt
fi