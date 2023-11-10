#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
mkdir -p $here/files
pushd $here/files
pwd
rsync -avz ukmonhelper2:prod/analysis/ ./analysis --delete
rsync -avz ukmonhelper2:prod/website/ ./website --delete
rsync -avz ukmonhelper2:prod/cronjobs/ ./cronjobs --delete
rsync -avz ukmonhelper2:prod/database/ ./database  --delete
rsync -avz ukmonhelper2:prod/setup/ ./setup --delete
rsync -avz ukmonhelper2:prod/utils/ ./utils --delete
rsync -avz ukmonhelper2:prod/share/ ./share --delete
rsync -avz ukmonhelper2:prod/static_content/ ./static_content --delete
rsync -avz ukmonhelper2:prod/ukmon_pylib/ ./ukmon_pylib --exclude=__pycache__ --exclude=.pytest_cache --delete
popd