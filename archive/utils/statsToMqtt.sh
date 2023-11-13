#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here
if [ "$(hostname)" == "wordpresssite" ] ; then
    source /home/bitnami/venvs/openhabstuff/bin/activate
    python $here/statsToMqtt.py
    diskpct=$(df / |tail -1| awk '{print $5 }' | sed 's/%//g')
    if [ $diskpct -gt 90 ] ; then 
        /home/bitnami/src/maintenance/mysql_checks.sh
        msg="$(hostname) diskspace was ${diskpct}%"
        subj="Diskspace alert for $(hostname)"
        hn="$(hostname)@aws"
        python -c "from meteortools.utils.sendAnEmail import sendAnEmail;sendAnEmail('markmcintyre99@googlemail.com', '$msg', '$subj', '$hn')"
    fi
elif [ "$(hostname)" == "ukmcalcserver" ] ; then
    source /home/ec2-user/venvs/wmpl/bin/activate
    python $here/statsToMqtt.py
    diskpct=$(df / |tail -1| awk '{print $5 }' | sed 's/%//g')
    if [ $diskpct -gt 90 ] ; then 
        msg="$(hostname) diskspace is ${diskpct}%"
        subj="Diskspace alert for $(hostname)"
        hn="$(hostname)@aws"
        python -c "from meteortools.utils.sendAnEmail import sendAnEmail;sendAnEmail('markmcintyre99@googlemail.com', '$msg', '$subj', '$hn')"
    fi
else
    source $here/../config.ini >/dev/null 2>&1
    conda activate $HOME/miniconda3/envs/${WMPL_ENV}
    export PYTHONPATH=$SRC/ukmon_pylib:$PYTHONPATH
    python -m metrics.statsToMqtt
    diskpct=$(df / |tail -1| awk '{print $5 }' | sed 's/%//g')
    if [ $diskpct -gt 90 ] ; then 
        msg="$(hostname) diskspace is ${diskpct}%"
        subj="Diskspace alert for $(hostname)"
        hn="$(hostname)@aws"
        python -c "from meteortools.utils.sendAnEmail import sendAnEmail;sendAnEmail('markmcintyre99@googlemail.com', '$msg', '$subj', '$hn')"
    fi
fi 
