#!/bin/bash

if [ $# -lt 2 ] ; then
    fn=$DATADIR/dailyreports/latest.txt
else 
    fn=$1
fi 
cat $1 | while read i
do
	pth=$(echo $i | awk -F, '{print $2}') 
	#thispth=${pth:28:200}
    thispth=$pth
	orbname=$(basename $thispth)
	orbn=${orbname:0:15}
	fullname=${thispth}${orbn}_trajectory.pickle
	cat cftpd_templ.json | sed "s|KEYGOESHERE|${fullname}|g" > tmp.json
    echo $orbn
	aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --invocation-type Event --log-type Tail  --payload file://./tmp.json  --region eu-west-2 --cli-binary-format raw-in-base64-out res.log
done
