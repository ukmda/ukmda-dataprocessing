#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}
cd $here

fn=$DATADIR/dailyreports/latest.txt
profile=ukmonshared
bucket=ukmda-shared

if [ "$1" != "" ] ; then fn=$1 ; fi

cat $fn | while read i
do
	pth=$(echo $i | awk -F, '{print $2}') 
	#thispth=${pth:28:200}
    thispth=$pth
	orbname=$(basename $thispth)
	orbn=${orbname:0:15}
	fullname=${thispth}/${orbn}_trajectory.pickle
	cat cftpd_templ.json | sed "s|ukmda-shared|${bucket}|g" | sed "s|KEYGOESHERE|${fullname}|g" > tmp.json
    echo $orbn $bucket $profile 
	aws lambda invoke --profile $profile --function-name getExtraOrbitFilesV2 --invocation-type Event --log-type Tail  --payload file://./tmp.json  --region eu-west-2 --cli-binary-format raw-in-base64-out res.log
done
