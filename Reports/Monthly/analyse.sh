#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ "$here" == *"prod"* ]] ; then
    echo sourcing prod config
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    echo sourcing dev config
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

if [ $# -lt 2 ] ; then
	echo Usage: analyse.sh GEM 2017
else
	$here/GENERATE_REPORTS_V2.r $1 $2
	echo .
	echo done
fi

