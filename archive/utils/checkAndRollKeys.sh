#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# script to check for keys older than 90 days and roll them 
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

export AWS_PROFILE=ukmonshared
python -m maintnenance.getUserAndKeyInfo autoroll
export AWS_PROFILE=