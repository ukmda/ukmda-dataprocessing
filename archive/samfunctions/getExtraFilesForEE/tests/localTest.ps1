# Copyright (C) 2018-2023 Mark McIntyre
sam build
sam local invoke --profile ukmda_admin -e tests\testEvent.json 
#sam local invoke --profile ukmda_admin -e tests\testEvent2.json 