# test 
aws lambda invoke --profile ukmda_admin --function-name ftpToUkmon --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
Start-Sleep 2
aws s3 ls s3://ukmda-shared/matches/single/new/
aws s3 cp s3://ukmda-shared/matches/single/new/ukmon_UK0006_20230202_173030_429632.csv ./tests/remoteResult.txt
bash -c "diff ./tests/expected_results.txt ./test/remoteResult.txt"