#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
	echo Usage: analyse.sh GEM 2017
else
    cd ${RCODEDIR}
	./GENERATE_REPORTS_V2.r $1 $2
	echo .
    cd $here
	echo done
fi

