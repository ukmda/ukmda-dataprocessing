# test the lambda

sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e ./test/testEvent.json
start-sleep 1
aws s3 cp s3://ukmon-shared/matches/single/new/ukmon_UK0006_20221104_170703_850082.csv ./test/new_data.txt
bash -c "diff ./test/expected_results.txt ./test/new_data.txt"