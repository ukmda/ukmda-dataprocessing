sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e tests\testEvent.json 
sam local invoke --profile ukmonshared -e tests\testEvent2.json 