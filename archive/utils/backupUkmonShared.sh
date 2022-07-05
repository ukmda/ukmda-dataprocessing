#!/bin/bash

# run this from a PC with enough network oomph. NOT a T3.micro!

# add folders here and in BackupRunner's userdata script if there are new folders created on ukmon-shared

for fldr in admin consolidated fireballs kmls videos matches archive
do 
    /usr/bin/time /usr/bin/aws s3 sync s3://ukmon-shared/$fldr s3://ukmon-shared-backup/$fldr 
done 

