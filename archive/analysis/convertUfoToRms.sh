#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Convert a month's worth of UFO data to RMS format
#
# Parameters:
#   month to process in yyyymm format
#
# Consumes:
#   UFO format data A.xml files
#
# Produces:
#   RMS format FTPdetect and platepars_all files, one per day

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

# get the date to operate for
if [ $# -eq 0 ]; then
    ym=$(date +%Y%m%d)
else
    ym=$1
fi

logger -s -t convertUfoToRms "starting"

python -m converters.UFOAtoFTPdetect $ym 30

logger -s -t convertUfoToRms "finished"