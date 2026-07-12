# test the lambda

Remove-Item ./tests/new_data.txt
sam local invoke --profile ukmda_admin -e ./tests/testEvent.json
start-sleep 1
aws s3 cp s3://ukmda-shared/matches/single/new/ukmda_UK0006_20240811_201327_827902.csv ./tests/new_data.txt --profile ukmda_admin
bash -c "diff ./tests/expected_results.txt ./tests/new_data.txt"