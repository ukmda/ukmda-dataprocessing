#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# bash script to update the keyfile to remove plaintext AWS security details
#

targ=$1

ls -1d /var/sftp/$targ* | while read i  
do
    if [ -f $i/live.key ] ; then
        echo -n "$i "
        \cp $i/live.key $i/live.key.old 
        cat $i/live.key | grep -v "ACCESS_KEY" > $i/live.key.new
        \mv -f $i/live.key.new $i/live.key
    fi
done
