#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# this script reads a list of logically-deleted trajectories from the sqlite database
# and moves the corresponding pickle and report data to a backup area
# These trajectories are generally duplicated events

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

cd ${DATADIR}/distrib

startdt=$(date --date="-$MATCHSTART days" '+%Y%m%d-080000')
jdt_min=$(python -c "from wmpl.Utils.TrajConversions import datetime2JD;import datetime;print(datetime2JD(datetime.datetime.strptime('$startdt', '%Y%m%d-%H%M%S')))")

echo "checking main storage"
sqlite3 trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    echo $trajdir
    aws s3 ls ${UKMONSHAREDBUCKET}/matches/RMSCorrelate/$trajdir/ | awk -F " " '{print $4}' | while read fname; do
       aws s3 mv ${UKMONSHAREDBUCKET}/matches/RMSCorrelate/$trajdir/$fname ${UKMONSHAREDBUCKET}/matches/duplicates/$trajdir/$fname
    done 
done

echo "checking website"
sqlite3 trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    yr=${trajdir:13:4}
    trajpth=${trajdir:18}
    echo $trajdir
    webloc=$WEBSITEBUCKET/reports/${yr}/orbits/$trajpth
    newloc=${UKMONSHAREDBUCKET}/matches/duplicates/reports/${yr}/orbits/$trajpth
    aws s3 ls $webloc/ | awk -F " " '{print $4}' | while read fname; do
       aws s3 mv $webloc/$fname $newloc/$fname
    done 
done

echo "checking fullcsv"
sqlite3 trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    yr=${trajdir:13:4}
    trajpth=${trajdir:34:19}
    csvname=$(echo $trajpth | sed 's/_/-/g')
    echo $csvname
    csvloc=${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv
    newloc=${UKMONSHAREDBUCKET}/matches/duplicates/csvs/${yr}
    aws s3 ls $csvloc/ | awk -F " " '{print $4}' | grep $csvname | while read fname; do
       aws s3 mv $csvloc/$fname $newloc/$fname
    done 
done
