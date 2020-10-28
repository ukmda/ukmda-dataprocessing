#!/bin/bash

if [ $# -lt 2 ] ; then
	echo Usage: analyse.sh GEM 2017
else
	./GENERATE_REPORTS_V2.r $1 $2
	echo .
	echo done generating reports, now copying them
	if [ -d REPORTS/$2/$1 ] ; then 
		mkdir -p ~/data/analysis/$2/$1
		cp REPORTS/$2/$1/* ~/data/analysis/$2/$1
	else
		echo nothing to copy - no output created!
	fi
	echo done
fi

