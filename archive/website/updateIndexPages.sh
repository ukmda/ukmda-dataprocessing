#!/bin/bash
#
# Updates the trajectory day, month and year index pages
#
# Parameters
#   the dailyreport file to use
#
# Produces
#   Updated indexes, pushed to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate



if [ $# -eq 0 ]; then
    dailyrep=$(ls -1tr $DATADIR/dailyreports/20* | tail -1)
else
    dailyrep=$1
fi
trajlist=$(cat $dailyrep | awk -F, '{print $2}')

logger -s -t updateIndexPages "Updating indexes"
for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:8} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for dtd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${dtd}
done
rm /tmp/days.txt

for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:6} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for dtd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${dtd}
done
rm /tmp/days.txt

for traj in $trajlist ; do bn=$(basename $traj); echo ${bn:0:4} >> /tmp/days.txt ; done
daystodo=$(cat /tmp/days.txt | sort | uniq)
for ytd in $daystodo
do
    $SRC/website/createOrbitIndex.sh ${ytd}
done
rm /tmp/days.txt

logger -s -t updateIndexPages "Finished"