#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to check for keys older than 90 days and roll them 
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t $(basename $0 .sh) "starting"

python -m maintenance.getUserAndKeyInfo autoroll


logger -s -t $(basename $0 .sh) "finished"
