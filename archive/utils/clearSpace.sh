#!/bin/bash
#
# script to update match data each night and then recalc any necessary orbits

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/$WMPL_ENV/bin/activate

logger -s -t cleanSpace "starting"

logger -s -t cleanSpace "clean up old logs"
find $SRC/logs -name "nightly*.gz" -mtime +60 -exec rm -f {} \;
find $SRC/logs -name "nightly*.log" -mtime +7 -exec gzip {} \;

find $SRC/logs/distrib -name "*.log" -mtime +30 -exec rm -f {} \;

find $SRC/logs -name "backup*.log" -mtime +30 -exec rm -f {} \;
find $SRC/logs -name "getImo*.log" -mtime +70 -exec rm -f {} \;
find $SRC/logs -name "gather*.log" -mtime +130 -exec rm -f {} \;

logger -s -t cleanSpace "clean up old trajdbs"
find $DATADIR/trajdb -name "*.gz" -mtime +30 -exec rm -f {} \;

logger -s -t cleanSpace "clean up old files from browse"
find $DATADIR/browse/annual -name "*.csv" -mtime +40 -exec rm -f {} \;
find $DATADIR/browse/monthly -name "*.csv" -mtime +40 -exec rm -f {} \;
find $DATADIR/browse/daily -name "*.csv" -mtime +40 -exec rm -f {} \;
find $DATADIR/browse/showers -name "*.csv" -mtime +40 -exec rm -f {} \;

logger -s -t cleanSpace "finished"
