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
sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    echo $trajdir
    moved=0
    aws s3 ls ${UKMONSHAREDBUCKET}/matches/RMSCorrelate/$trajdir/ | awk -F " " '{print $4}' | while read fname; do
       aws s3 mv ${UKMONSHAREDBUCKET}/matches/RMSCorrelate/$trajdir/$fname ${UKMONSHAREDBUCKET}/matches/duplicates/$trajdir/$fname --quiet
       moved=1
    done 
    [ $moved == 1 ] && echo moved $trajdir
done

echo "checking website"
sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    yr=${trajdir:13:4}
    trajpth=${trajdir:18}
    echo $trajdir
    webloc=$WEBSITEBUCKET/reports/${yr}/orbits/$trajpth
    newloc=${UKMONSHAREDBUCKET}/matches/duplicates/reports/${yr}/orbits/$trajpth
    moved=0
    aws s3 ls $webloc/ | awk -F " " '{print $4}' | while read fname; do
       aws s3 mv $webloc/$fname $newloc/$fname --quiet
       moved=1
    done 
    [ $moved == 1 ] && echo moved $trajdir
done

echo "checking fullcsv"
sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    yr=${trajdir:13:4}
    trajpth=${trajdir:34:19}
    csvname=$(echo $trajpth | sed 's/_/-/g')
    echo $csvname
    csvloc=${UKMONSHAREDBUCKET}/matches/${yr}/fullcsv
    newloc=${UKMONSHAREDBUCKET}/matches/duplicates/csvs/${yr}
    moved=0
    aws s3 ls $csvloc/ | awk -F " " '{print $4}' | grep $csvname | while read fname; do
       aws s3 mv $csvloc/$fname $newloc/$fname --quiet
       moved=1
    done 
    [ $moved == 1 ] && echo moved $trajdir
done

echo "checking historic fullcsv just in case"
sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | while read traj ; do
    trajdir=$(dirname $traj)
    yr=${trajdir:13:4}
    trajpth=$(basename $trajdir)
    csvname=$(echo $trajpth | sed 's/_/-/g')
    echo $csvname
    csvloc=$DATADIR/orbits/${yr}/fullcsv/processed
    newloc=${UKMONSHAREDBUCKET}/matches/duplicates/csvs/${yr}
    moved=0
    ls -1 $csvloc/ | grep $csvname | while read fname; do
       aws s3 mv $csvloc/$fname $newloc/$fname --quiet
       moved=1
    done 
    [ $moved == 1 ] && echo moved $trajdir
    export trajpth
done

echo "checking consolidated matches"
lasttraj=$(sqlite3 $DATADIR/distrib/trajectories.db "select traj_file_path from trajectories where status=0 and jdt_ref > ${jdt_min} order by jdt_ref;" | tail -1)
trajdir=$(dirname $lasttraj)
yr=${trajdir:13:4}
trajpth=$(basename $trajdir)
matchcsv=$DATADIR/matched/matches-full-${yr}.csv
if [ $? == 0 ] ; then 
    python -c "from maintenance.dataMaintenance import removeDeletedTraj;removeDeletedTraj('$matchcsv')"
    python -m converters.toParquet $matchcsv
    aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matched/ --include "*" --exclude "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet
    aws s3 sync $DATADIR/matched/ $UKMONSHAREDBUCKET/matches/matchedpq/ --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet 
    aws s3 sync $DATADIR/matched/ $WEBSITEBUCKET/browse/parquet/  --exclude "*" --include "*.snap" --exclude "*.bkp" --exclude "*.gzip" --quiet

    srchcsv=$DATADIR/searchidx/${yr}-allevents.csv
    python -c "from maintenance.dataMaintenance import removeDeletedTraj;removeDeletedTraj('$srchcsv')"
    aws s3 sync  $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --exclude "*" --include "*allevents.csv" --quiet 
fi 

export AWS_PROFILE=ukmonshared # needed for mariadb connection details
echo "checking Mariadb Database"
python -c "from maintenance.dataMaintenance import removeDelTrajFromDb;removeDelTrajFromDb()"
unset AWS_PROFILE
done