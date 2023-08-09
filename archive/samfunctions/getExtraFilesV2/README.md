# getExtraFilesV2

Deploy this function into the EE account

```bash
sam build --profile ukmonshared --region eu-west-2
sam deploy --profile ukmonshared --region eu-west-2
```
to test it locally
```bash
sam local invoke --profile ukmonshared --region eu-west-2 -e tests/testEvent.json 
```

to deploy and test
```bash
sam deploy --profile ukmonshared --region eu-west-2
aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
```

# copyright
All code Copyright (C) 2018-2023 Mark McIntyre
