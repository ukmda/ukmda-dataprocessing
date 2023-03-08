# test consolidateFTPdetect
# Copyright (C) 2018-2023 Mark McIntyre
aws lambda invoke --profile ukmonshared --function-name consolidateFTPdetect --log-type Tail --cli-binary-format raw-in-base64-out --payload file://consolidateFTPdetectTest.json  --region eu-west-2 ./ftpdetect.log
aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/UK0029/UK0029_20221104_171920_151384/
