sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e tests\testEvent.json 