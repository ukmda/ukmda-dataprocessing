#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre


here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

[ -z $RUNTIME_ENV ] && RUNTIME_ENV=$1
envname=$(echo $RUNTIME_ENV | tr '[:upper:]' '[:lower:]')

cd $here/../static_content
if [ "$envname" == "prod" ] ; then
    AWSPROFILE=ukmonshared
else
    AWSPROFILE=Mark
fi 
for fldr in browse css data docs fonts js latest live search templates ; do 
    aws s3 sync $SRC/static_content/$fldr/ $WEBSITEBUCKET/$fldr/ --profile $AWSPROFILE 
done
aws s3 cp $SRC/website/templates/searchdialog.js $WEBSITEBUCKET/js/searchdialog.js --profile $AWSPROFILE

ls -1 *.html *.ico *.txt | while read i ; do 
    aws s3 cp $i $WEBSITEBUCKET/$i --profile $AWSPROFILE 
done 

ls -1 img/*.png img/*.svg | while read i;  do   
    aws s3 cp $i $WEBSITEBUCKET/$i --exclude "*ukmon*" --profile $AWSPROFILE 
done

