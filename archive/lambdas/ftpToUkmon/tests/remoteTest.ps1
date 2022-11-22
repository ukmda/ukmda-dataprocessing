# test consolidateFTPdetect
aws lambda invoke --profile ukmonshared --function-name ftpToUkmon --log-type Tail --cli-binary-format raw-in-base64-out --payload file://test/testEvent.json  --region eu-west-2 ./ftpdetect.log
Start-Sleep 2
aws s3 ls s3://ukmon-shared/matches/single/new/
aws s3 cp s3://ukmon-shared/matches/single/new/ukmon_UK0006_20221104_170703_850082.csv ./test/remoteResult.txt
bash -c "diff ./test/expected_results.txt ./test/remoteResult.txt"