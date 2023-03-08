#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# srclist should be a list of folders on S3 containing ftpdetects 
# eg
# matches/RMSCorrelate/UK0006/UK0006_20221210_163357_815689/
# matches/RMSCorrelate/UK0006/UK0006_20221201_163642_315379//

cat srclist.txt | while read i 
do
	echo $i 
	ftpname=$(aws s3 ls s3://ukmon-shared/${i}/ | grep FTPdetect | egrep -v "uncalibrated|filter|backup"  | awk -F " " '{print $4}')
	if [ "$ftpname" != "" ] ; then 
		fullname=$i/$ftpname
		cat cftpd_templ.json | sed "s|KEYGOESHERE|${fullname}|g" > tmp.json
		#cat tmp.json
		aws lambda invoke --profile ukmonshared --function-name consolidateFTPdetect --log-type Tail  --payload file://./tmp.json  --region eu-west-2 --cli-binary-format raw-in-base64-out res.log
	fi
done



