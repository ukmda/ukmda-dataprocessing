# Copyright (C) 2018-2023 Mark McIntyre
$here=$PSScriptRoot
# sam build --profile ukmonshared --region eu-west-1
sam local invoke --profile ukmonshared -e $here/test.json  --region eu-west-1 > $here/new_output.txt
windiff $here/expected_output.txt $here/new_output.txt

