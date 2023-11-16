#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre


here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

RUNTIME_ENV=$1
envname=$(echo $RUNTIME_ENV | tr '[:upper:]' '[:lower:]')

if [ "$envname" == "PROD" ] ; then
    for fldr in browse css data js fonts latest search templates ; do 
        aws s3 sync $SRC/static_content/$fldr/ $WEBSITEBUCKET/$fldr/ --profile ukmonshared --exclude "*ukmda*" --exclude "*ukmon*"
    done
    # copy dragontail.css constellation.js navbar.html favicon.ico
    aws s3 cp $SRC/static_content/css/dragontail_ukmda.css $WEBSITEBUCKET/css/dragontail.css --profile ukmonshared 
    aws s3 cp $SRC/static_content/js/constellation_ukmda.js $WEBSITEBUCKET/js/constellation.js --profile ukmonshared 
    aws s3 cp $SRC/static_content/templates/navbar_ukmda.html $WEBSITEBUCKET/templates/navbar.html --profile ukmonshared 
    aws s3 cp $SRC/static_content/favicon_ukmda.ico $WEBSITEBUCKET/favicon.ico --profile ukmonshared 
    aws s3 cp $SRC/website/templates/searchdialog-prod.js $WEBSITEBUCKET/data/searchdialog.js --profile ukmonshared 
    aws s3 cp $SRC/static_content/js/gtagadder_ukmda.js $WEBSITEBUCKET/js/gtagadder.js --profile ukmonshared 

    ls -1 img/*.png img/*.svg | while read i;  do   
        aws s3 cp $i $WEBSITEBUCKET/$i --exclude "*ukmon*" --profile ukmonshared 
    done
else
    echo "not implemented"
fi 

