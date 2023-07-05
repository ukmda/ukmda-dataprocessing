#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# bash script to update the ukmon helper ip address
#

targ=$1

ls -1d $targ* | while read i  
do
    if [ -f $i/ukmon.ini ] ; then
        echo -n $i
        echo cat $i/ukmon.ini | sed 's/3.8.65.98/3.11.55.160/g' > $i/ukmon.ini.new
        echo \mv -f $i/ukmon.ini.new $i/ukmon.ini
        grep UKMONHELPER $i/ukmon.ini
    fi
done
