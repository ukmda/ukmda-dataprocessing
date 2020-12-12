#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [ $# -lt 2 ] ; then
	echo Usage: analyse.sh GEM 2017
else
	source $here/config.ini >/dev/null 2>&1

	$here/GENERATE_REPORTS_V2.R $1 $2
	echo .
	
	if [ -d $here/REPORTS/$2/$1 ] ; then 
		echo "done generating graphs and tables, now copying them"
		mkdir -p $REPORTDIR/$2/$1
		cp $here/REPORTS/$2/$1/* $REPORTDIR/$2/$1
	else
		echo "nothing to copy - no output created!"
	fi
	echo done
	$here/updateMainIndex.sh

fi

