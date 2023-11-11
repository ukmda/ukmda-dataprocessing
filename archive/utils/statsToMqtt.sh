#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here
if [ "$(hostname)" == "wordpresssite" ] ; then
    source /home/bitnami/venvs/openhabstuff/bin/activate
    python $here/statsToMqtt.py
elif [ "$(hostname)" == "ukmcalcserver" ] ; then
    source /home/ec2-user/venvs/wmpl/bin/activate
    python $here/statsToMqtt.py
else
    source $here/../config.ini >/dev/null 2>&1
    conda activate $HOME/miniconda3/envs/${WMPL_ENV}
    export PYTHONPATH=$SRC/ukmon_pylib:$PYTHONPATH
    python -m metrics.statsToMqtt
fi 
