#
# Python script to create execMatching shell script to be run on the calc engine
#

import os
import sys
import datetime


shkey = os.getenv('UKMONSHAREDKEY')
shbucket = os.getenv('UKMONSHAREDBUCKET')
webkey = os.getenv('WEBSITEKEY')
webbucket = os.getenv('WEBSITEBUCKET')
if len(sys.argv) < 4:
    print('Usage: createDistribMatchingSh day1 day2 outfile')
    exit(1)
matchstart = int(sys.argv[1])
matchend = int(sys.argv[2])
outfname = sys.argv[3]

startdt = datetime.datetime.now() + datetime.timedelta(days=-matchstart)
enddt = datetime.datetime.now() + datetime.timedelta(days=-matchend)
print(startdt, enddt)
startdtstr = startdt.strftime('%Y%m%d-080000')
enddtstr = enddt.strftime('%Y%m%d-080000')
rundatestr = enddt.strftime('%Y%m%d')

yr = enddt.year
ym = enddt.strftime('%Y%m')

execmatchingsh = outfname 
with open(execmatchingsh, 'w') as outf:
    outf.write('#!/bin/bash\n')
    outf.write('source /home/ec2-user/venvs/wmpl/bin/activate\n')
    outf.write('export PYTHONPATH=/home/ec2-user/src/WesternMeteorPyLib:/home/ec2-user/src/ukmon_pylib/ukmon_pylib\n')
    outf.write('cd /home/ec2-user/data/RMSCorrelate\n')
    outf.write('df -h . \n')
    outf.write(f'source {shkey}\n')
    outf.write(f'time aws s3 sync {shbucket}/matches/RMSCorrelate/ . --exclude "*" --include "UK*" --quiet\n')
    outf.write('logger -s -t runMatching \"starting correlator\"\n')
    outf.write(f'time python -m wmpl.Trajectory.CorrelateRMS /home/ec2-user/data/RMSCorrelate/ -i 1 -l -r \"({startdtstr},{enddtstr})\"\n')
    outf.write('cd /home/ec2-user/data/RMSCorrelate\n')
    outf.write(f'time python -m traj.distributeCandidates ${rundatestr} ./candidates ${shbucket}/matches/distrib\n')
    outf.write('logger -s -t runMatching \"done\"\n')
