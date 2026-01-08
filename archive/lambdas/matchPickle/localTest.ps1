# Copyright (C) 2018-2023 Mark McIntyre
sam build --profile ukmonshared --region eu-west-1
sam local invoke --profile ukmonshared -e testEvent.json  --region eu-west-1
