# test the lambda

sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e ./tests/testEvent.json
start-sleep 1
aws s3 cp s3://ukmon-shared/matches/single/new/ukmon_UK0006_20221104_170703_850082.csv ./tests/new_data.txt
bash -c "diff ./tests/expected_results.txt ./tests/new_data.txt"