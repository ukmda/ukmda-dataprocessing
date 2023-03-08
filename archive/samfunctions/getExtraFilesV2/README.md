# getExtraFilesV2

Deploy this function into the markmcintyreastro account

```bash
sam build --profile default
sam deploy --profile default
```
to test it locally
```bash
sam local invoke --profile default -e tests/testEvent.json 
```

to deploy and test
```bash
sam deploy --profile default
aws lambda invoke --profile default --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
```

# copyright
All code Copyright (C) 2018-2023 Mark McIntyre
