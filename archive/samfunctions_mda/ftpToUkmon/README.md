# getExtraFilesV2

Deploy this function into the markmcintyreastro account

To build 

```bash
sam build --profile ukmonshared
```
Test locally
```bash
sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e ./tests/testEvent.json
```
Deploy
```bash
sam deploy --profile ukmonshared
```
remote test
```bash
aws lambda invoke --profile ukmonshared --function-name ftpToUkmon --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log
```

# Copyright
All code Copyright (C) 2018-2023 Mark McIntyre