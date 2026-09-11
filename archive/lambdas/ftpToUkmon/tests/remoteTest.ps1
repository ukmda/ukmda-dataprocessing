# test 
aws lambda invoke --profile ukmda_admin --function-name ftpToUkmon --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
Start-Sleep 2
aws s3 cp s3://ukmda-shared/matches/single/new/ukmda_UK0006_20240811_201327_827902.csv ./tests/new_data.txt --profile ukmda_admin
bash -c "diff ./tests/expected_results.txt ./test/remoteResult.txt"