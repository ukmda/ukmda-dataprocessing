# Copyright (C) 2018-2023 Mark McIntyre
$here=$PSScriptRoot
#sam build --profile ukmonshared
sam local invoke --profile ukmonshared -e $here/test.json
