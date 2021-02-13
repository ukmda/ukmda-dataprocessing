#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

if [ $# -lt 2 ] ; then
	echo Usage: analyse.sh GEM 2017
else
    cd ${RCODEDIR}
	./GENERATE_REPORTS_V2.r $1 $2
	echo .
    cd $here
	echo done
fi

