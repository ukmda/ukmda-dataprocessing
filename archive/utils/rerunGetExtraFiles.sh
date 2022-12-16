#!/bin/bash

cat $DATADIR/dailyreports/latest.txt | while read i
do
	pth=$(echo $i | awk -F, '{print $2}') 
	thispth=${pth:28:200}
	orbname=$(basename $thispth)
	orbn=${orbname:0:15}
	fullname=${thispth}/${orbn}_trajectory.pickle
	cat cftpd_templ.json | sed "s|KEYGOESHERE|${fullname}|g" > tmp.json
	aws lambda invoke --profile Mark --function-name getExtraOrbitFilesV2 --log-type Tail  --payload file://./tmp.json  --region eu-west-2 --cli-binary-format raw-in-base64-out res.log
done
